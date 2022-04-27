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
        entity_list.append(Entity(entity['entityID'], entity_name, entity['entityType']))

    return entity_list


if __name__ == "__main__":
    project_name = "benchmark"
    input_path = "D:/scitool/SciTools/scripts/benchmark_entity.json"
    output_path = "D:/scitool/SciTools/scripts/"

    entity_list = deal(input_path)
    output(entity_list, output_path + "understand_" + project_name + "_entity.json",  "entity", project_name)

