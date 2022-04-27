import json
import sqlite3
import re
import math

def Entity(entityID, entityName, entityType, entityFile = None, startLine = -1, startColumn = -1, endLine = -1, endColumn = -1):
    entity = dict()
    entity['entityID'] = entityID
    entity['entityName'] = entityName
    entity['entityType'] = entityType
    entity['entityFile'] = entityFile
    entity['startLine'] = startLine
    entity['startColumn'] = startColumn
    entity['endLine'] = endLine
    entity['endColumn'] = endColumn
    return entity


def Dependency(dependencyType, dependencySrcID, dependencydestID, startLine = -1, startColumn = -1, endLine = -1, endColumn = -1):
    dependency = dict()
    dependency['dependencyType'] = dependencyType
    dependency['dependencySrcID'] = dependencySrcID
    dependency['dependencyDestID'] = dependencydestID
    dependency['startLine'] = startLine
    dependency['startColumn'] = startColumn
    dependency['endLine'] = endLine
    dependency['endColumn'] = endColumn
    return dependency


def get_all_table_name(cur):
    # 获取表名，保存在tab_name列表
    cur.execute("select name from sqlite_master where type='table'")
    tab_name = cur.fetchall()
    tab_name = [line[0] for line in tab_name]
    # 获取表的列名（字段名），保存在col_names列表,每个表的字段名集为一个元组
    col_names = []
    for line in tab_name:
        cur.execute('pragma table_info({})'.format(line))
        col_name = cur.fetchall()
        col_name = [x[1] for x in col_name]
        col_names.append(col_name)
        col_name = tuple(col_name)
    print(tab_name)
    print(col_names)


def sourcetrail_get_node(cur, field_separator, language):
    # 启用了四个表来完成操作，分别为node, occurrence, file, source_location
    # table information:
    # node: ['id', 'type', 'serialized_name']
    # file: ['id', 'path', 'language', 'modification_time', 'indexed', 'complete', 'line_count']
    # source_location: ['id', 'file_node_id', 'start_line', 'start_column', 'end_line', 'end_column', 'type'],
    # occurrence: ['element_id', 'source_location_id']

    cur.execute("select id,type,serialized_name from node")
    node_infor = cur.fetchall()
    cur.execute("select element_id,source_location_id from occurrence")
    element_to_source = cur.fetchall()
    cur.execute("select id, path from file")
    file_infor = cur.fetchall()
    cur.execute("select id, file_node_id, start_line, start_column, end_line, end_column from source_location")
    node_location_infor = cur.fetchall()

    element_to_source_dict = dict()
    for element in element_to_source:
        element_to_source_dict[element[0]] = element[1]
    file_dict = dict()
    for file in file_infor:
        file_dict[file[0]] = file[1]

    node_location_dict = dict()
    for node in node_location_infor:
        node_location_dict[node[0]] = [node[1], node[2], node[3], node[4], node[5]]

    node_list = list()
    for node in node_infor:
        type = resolve_node_type(node[1])
        if type == 'FILE':
            name = node[2].replace("/\tm", "")
            name = name.replace("\tn", "")
            name = name.replace("\ts", "")
            name = name.replace("\tp", "")
            name = name.replace(field_separator, "")

        else:
            name = resolve_node_name(node[2], language)

        if node[0] in element_to_source_dict.keys():
            source_id = element_to_source_dict[node[0]]
            node_location = node_location_dict[source_id]
            node_file_path = file_dict[node_location[0]]
            node_file_path = node_file_path.replace(field_separator, "")
            node_list.append(Entity(node[0], name, type, node_file_path, node_location[0], node_location[1], node_location[2], node_location[3]))
        else:
            node_list.append(Entity(node[0], name, type))
    return node_list


def resolve_node_name(name: str, language):
    META_DELIMITER = "\tm"
    NAME_DELIMITER = "\tn"
    PARTS_DELIMITER = "\ts"
    SIGNATURE_DELIMITER = "\tp"

    name = re.sub("(.*)" + META_DELIMITER, "", name, flags=0)
    name = name.replace(PARTS_DELIMITER + SIGNATURE_DELIMITER, "")

    name = name.replace(NAME_DELIMITER, ".")

    if (name.find(PARTS_DELIMITER)!=-1) & (name.find(SIGNATURE_DELIMITER)!=-1):
        name = name[0:name.find(PARTS_DELIMITER)]
    if language == 'cpp':
        name = name.split(".")
        name = "::".join(name)
    return name


def resolve_node_type(type: int):
    NodeKind = ["UNKNOWN", "TYPE", "BUILTIN_TYPE", "MODULE", "NAMESPACE",
            "PACKAGE", "STRUCT", "CLASS", "INTERFACE", "ANNOTATION",
            "GLOBAL_VARIABLE", "FIELD", "FUNCTION", "METHOD",
            "ENUM", "ENUM_CONSTANT", "TYPEDEF", "TYPE_PARAMETER",
            "FILE", "MACRO", "UNION"]
    return NodeKind[int(math.log(type, 2))]


def sourcetrail_get_edge(cur):
    EdgeKind = ["MEMBER,", "TYPE_USAGE", "USAGE", "CALL", "INHERITANCE",
                "OVERRIDE", "TYPE_ARGUMENT", "TEMPLATE_SPECIALIZATION",
                "INCLUDE", "IMPORT", "MACRO_USAGE", "ANNOTATION_USAGE", "UNKNOWN"]
    cur.execute("select id, type, source_node_id, target_node_id from edge")
    edge_infor = cur.fetchall()
    edge_list = list()

    for edge in edge_infor:
        edge_list.append(Dependency(EdgeKind[int(math.log(edge[1], 2))], edge[2], edge[3]))
    return edge_list


def output(info_list: list, json_path: str, type:str, projectname: str):
    file = dict()
    file["schemaVersion"] = 1.0
    file[type] = info_list
    file['projectName'] = projectname
    dependency_str = json.dumps(file, indent=4)
    with open(json_path, 'w') as json_file:
        json_file.write(dependency_str)


if __name__ == "__main__":

    # need: projectname, db_path, field_separator, language, outputFile
    projectname = "bitcoin"
    language = "cpp"
    root = "C:/Users/ding7/Desktop/"
    
    field_separator = "D:/gitrepo/" + language + "/" + projectname +"/"
    db_path = "D:/gitrepo/" + language + "/" + projectname + "/" + projectname + ".srctrldb"

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    entityList = sourcetrail_get_node(cur, field_separator, language)
    dependencyList = sourcetrail_get_edge(cur)

    entity_json_path = root + "sourcetrail_" + projectname +"_entity.json"
    dependency_json_path = root + "sourcetrail_" +projectname +"_dependency.json"

    output(entityList, entity_json_path, "entity", projectname)
    output(dependencyList, dependency_json_path, "dependency", projectname)
