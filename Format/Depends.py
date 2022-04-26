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

def depends_deal(input_path, projectName, root,  absolutePath):
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    entityList = list()

    for entity in data['variables']:
        operator_escape_character = False
        if entity.__contains__("operator /"):
            operator_escape_character = True
            entity = entity.replace("operator /", "operator")
            print(entity)

        entity = entity.replace("/", "\"")
        entity = entity.replace("\\", "/")
        entity = entity.replace(absolutePath, "")
        entity = "{" + entity + "}"

        # dict_keys(['name', 'filename', 'type', 'id', 'line'])
        convertedDict = ast.literal_eval(entity)
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
        if (language == 'cpp') & (convertedDict['type']!= 'file'):
            name = name.split(".")
            name = "::".join(name)
        entityList.append(Entity(id, name, convertedDict['type'],
                                        filename, line))

    dependencyList = list()
    for dependency in data['cells']:
        for dep in dependency['values']:
            dependencyList.append(Dependency(dep, dependency['src'], dependency['dest']))

    entity_file = dict()
    entity_file["schemaVersion"] = 1.0
    entity_file['entity'] = entityList
    entity_file['projectName'] = projectName
    entity_json_path = root + "depends_" + projectName + "_entity.json"
    entity_str = json.dumps(entity_file, indent=4)
    with open(entity_json_path, 'w') as json_file:
        json_file.write(entity_str)

    dependency_file = dict()
    dependency_file["schemaVersion"] = 1.0
    dependency_file['dependency'] = dependencyList
    dependency_file['projectName'] = projectName
    dependency_json_path = root + "depends_" + projectName + "_dependency.json"
    dependency_str = json.dumps(dependency_file, indent=4)
    with open(dependency_json_path, 'w') as json_file:
        json_file.write(dependency_str)


if __name__ == "__main__":
    # need: input_path , project_name , output_path
    input_path = "C:/Users/ding7/Desktop/consistence anlysis/source_input/depends_python/boto3.json"
    project_name = "boto3"
    output_path =  "C:/Users/ding7/Desktop/consistence anlysis/input/python/"
    field_separator = "D:/gitrepo/python/boto3/"
    language = ""
    depends_deal(input_path, project_name, output_path, field_separator, language)
