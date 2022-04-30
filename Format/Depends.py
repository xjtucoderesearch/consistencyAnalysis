import json
import ast

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

def output(info_list: list, json_path: str, type:str, projectname: str):
    file = dict()
    file["schemaVersion"] = 1.0
    file[type] = info_list
    file['projectName'] = projectname
    dependency_str = json.dumps(file, indent=4)
    with open(json_path, 'w') as json_file:
        json_file.write(dependency_str)

def depends_deal(input_path, projectName, root,  absolutePath, language):
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    entityList = list()

    for entity in data['variables']:
        operator_escape_character = False
        if entity.__contains__("operator /"):
            operator_escape_character = True
            entity = entity.replace("operator /", "operator")
            print(entity)

        entity = entity.replace("\n", "")
        entity = entity.replace("/", "\"")
        entity = entity.replace("\\", "/")
        entity = entity.replace(absolutePath, "")
        entity = "{" + entity + "}"

        # dict_keys(['name', 'filename', 'type', 'id', 'line'])
        try:
            convertedDict = ast.literal_eval(entity)
        except:
            continue

        line = int(convertedDict['line'])
        id = int(convertedDict['id'])

        name = convertedDict['name']
        if name == "":
            name = None
        if operator_escape_character:
            name = name.replace("operator", "operator /")
            print(name)

        filename = convertedDict['filename']
        if filename == "":
            filename = None
        if (language == 'cpp') & (convertedDict['type'] != 'File'):
            if not name == None:
                name = name.split(".")
                name = "::".join(name)
        if language == 'python':
            kind = convertedDict['type']
            if kind == "File":
                continue
            else:
                if not (filename is None) | name.__contains__("/"):
                    if not len(filename) == 0:
                        if not filename.__contains__("__init__"):
                            filename = filename.replace(".py", "")
                            if not filename.__contains__("/"):
                                name = filename + "." + name
                            else:
                                filename = filename.split("/")
                                add_scope = ".".join(filename)
                                filename = filename[0:len(filename) - 1]
                                filename = ".".join(filename)
                                name = name.replace(filename, add_scope)

        entityList.append(Entity(id, name, convertedDict['type'], filename, line))

    dependencyList = list()
    for dependency in data['cells']:
        for dep in dependency['values']:
            dependencyList.append(Dependency(dep, dependency['src'], dependency['dest']))

    entity_json_path = root + "depends_" + projectName + "_entity.json"
    dependency_json_path = root + "depends_" + projectName + "_dependency.json"
    output(entityList, entity_json_path, "entity", projectName)
    output(dependencyList, dependency_json_path, "dependency", projectName)


if __name__ == "__main__":
    # need: input_path , project_name , output_path
    project_name = "keras"
    input_path = "E:/depends/keras.json"

    output_path = "C:/Users/ding7/Desktop/"
    field_separator = "D:/gitrepo/python/" + project_name + "/"
    language = "python"
    depends_deal(input_path, project_name, output_path, field_separator, language)
