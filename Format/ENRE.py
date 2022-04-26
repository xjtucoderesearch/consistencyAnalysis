import json


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


def output(info_list: list, json_path: str, type:str, projectname: str):
    file = dict()
    file["schemaVersion"] = 1.0
    file[type] = info_list
    file['projectName'] = projectname
    dependency_str = json.dumps(file, indent=4)
    with open(json_path, 'w') as json_file:
        json_file.write(dependency_str)


def python_deal(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        info = json.load(file)
    entity_list = list()
    dependency_list = list()
    for entity in info['Entities']:
        entity_list.append(Entity(entity['id'], entity['longname'], entity['ent_type']))
    for dependency in info['Dependencies']:
        dependency_list.append(Dependency(dependency['kind'], dependency['src'], dependency['dest'], dependency['lineno']))
    return entity_list, dependency_list


def java_deal(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        enre_result = json.load(file)
    print(enre_result.keys())
    nodes = enre_result['variables']
    edges = enre_result['cells']

    node_list = list()
    edge_list = list()

    for node in nodes:
        if node['external'] == True:
            break
        node_list.append(Entity(node['id'], node['qualifiedName'], node['category']))
    for edge in edges:
        values = edge['values']
        for value in values.keys():
            type = value
        edge_list.append(Dependency(type, edge['src'],edge['dest']))

    return node_list, edge_list


def cpp_deal(entity_path, dependency_path):
    with open(entity_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    entity_list = list()
    for entity in data:
        entity_list.append(Entity(entity['id'], entity['qualifiedName'], entity['entityType'], entity['entityFile'],
                                 entity['startLine'], entity['startColumn'], entity['endLine'], entity['endColumn']))
    with open(dependency_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    dependency_list = list()
    for dependency in data:
        # dict_keys(['type', 'src', 'dest'])
        dependency_list.append(Dependency(dependency['type'], dependency['src'], dependency['dest']))
    return entity_list, dependency_list





if __name__ == "__main__":
    language = ""
    projectname = ""
    input_path = ""
    output_path = ""

    if language == "cpp":
        entity_list, dependency_list = cpp_deal(input_path + "_entity.json", input_path + "_dependency.json")
    elif language == "java":
        entity_list, dependency_list = java_deal(input_path)
    elif language == "python":
        entity_list, dependency_list = python_deal(input_path)

    if (language == 'cpp') | (language == 'java') | (language == 'python'):
        output(entity_list, output_path + projectname + "_entity.json",  "entity", projectname)
        output(dependency_list, output_path + projectname + "_dependency.json", "dependency", projectname)
