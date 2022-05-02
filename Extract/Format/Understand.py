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


def output(info_list: list, json_path: str, type:str, projectname: str):
    file = dict()
    file["schemaVersion"] = 1.0
    file[type] = info_list
    file['projectName'] = projectname
    dependency_str = json.dumps(file, indent=4)
    with open(json_path, 'w') as json_file:
        json_file.write(dependency_str)


def deal(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    entity_list = list()
    for entity in data['entity']:
        entity_name = entity['entityName']
        if entity['entityType'] == "File":
            entity_name = entity_name.replace("\\", "/")
        entity_list.append(Entity(entity['entityID'], entity_name, entity['entityType'],
                                  entity['entityFile'], entity['startLine'], entity['startColumn'],
                                  entity['endLine'], entity['endColumn']))
    return entity_list


def understand(input_path, output_path, project_name):
    entity_list = deal(input_path)
    output(entity_list, output_path + "understand_" + project_name + "_dependency.json", "dependency", project_name)

if __name__ == "__main__":
    project_name = "keras"
    input_path = "C:/Users/ding7/Desktop/consistencyAnalysis/input_dir/" + project_name + "/understand_" + project_name + "_entity.json"
    input_path = "D:/scitool/SciTools/scripts/understand_keras_dependency.json"
    output_path = "C:/Users/ding7/Desktop/consistencyAnalysis/input_dir/" + project_name + "/"

    entity_list = deal(input_path)
    output(entity_list, output_path + "understand_" + project_name + "_dependency.json",  "dependency", project_name)

