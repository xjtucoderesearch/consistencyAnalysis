import json
import logging
import os
import pickle
from pathlib import Path
import networkx as nx
import Tree
from Tree import nameTree
from datetime import datetime

class Batch:
    def __init__(self, language, project_name, separation):
        self.language = language
        self.project_name = project_name
        self.separation = separation
        with open("mappings/" + language + "_" + "map.json", 'r') as file:
            mapping = json.load(file)
        self.entity_map = mapping['entity_map']
        self.dependency_map = mapping['dependency_map']
        self.specifier_list = {
            'cpp': ['public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown', 'const', 'virtual', 'explicit', 'c ', 'default'],
            'java': ['java', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown'],
            'python': ['python', 'possible', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown']
        }
        output_path = f"./output_dir/{self.project_name}"
        isOutputExist = os.path.exists(output_path)
        if not isOutputExist:
            # Create a new directory because it does not exist
            os.makedirs(output_path)
        pickle_path = f"./pickle_dir/{self.project_name}"
        isPickleExist = os.path.exists(pickle_path)
        if not isPickleExist:
            os.makedirs(pickle_path)

    def resolveType(self, type: str) -> str:
        for specifier in self.specifier_list[self.language]:
            type = type.replace(specifier, "")
        type = type.strip()
        return type

    def load_entity_file(self, path):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data['entity']

    def load_dependency_file(self, path):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data['dependency']

    def getType(self, dataset_name, entity_type):
        entity_type = entity_type.lower()
        if dataset_name == "understand":
            entity_type = self.resolveType(entity_type)
        return self.entity_map[dataset_name][entity_type]

    def build_trees(self, data, dataset_name):
        pickle_path = f"./pickle_dir/{self.project_name}/{dataset_name}_{self.project_name}.pickle"
        my_file = Path(pickle_path)
        if my_file.is_file():
            return
        # os.path.isfile(target)
        forest = dict()
        logging.info(f"start load {dataset_name} data:")
        start = datetime.now()
        for entity in data:
            en = entity['entityName']
            entity_type = self.getType(dataset_name, entity['entityType'])
            if not en == None:
                if entity_type not in forest.keys():
                    forest[entity_type] = nameTree()
                forest[entity_type].insert(en.split(self.separation), data.index(entity))

        logging.info(f"load {dataset_name} costs: {datetime.now() - start}.")
        with open(pickle_path, 'wb') as file:
            pickle.dump(forest, file)

    def entity_compare(self, l_dataset_name, r_dataset_name):
        pickle_path = f"./pickle_dir/{self.project_name}/{l_dataset_name}_{self.project_name}.pickle"
        my_file = Path(pickle_path)
        if my_file.is_file():
            with open(pickle_path, 'rb') as file:
                l_forest = pickle.load(file)
        with open(f"./pickle_dir/{self.project_name}/{r_dataset_name}_{self.project_name}.pickle", 'rb') as file:
            r_forest = pickle.load(file)

        logging.info(f"Start compare data:")
        compare_start = datetime.now()
        Equal = list()
        for key in l_forest.keys():
            if key in r_forest.keys():
                logging.info(f"Start compare {key} tries:")
                compare = Tree.Compare()
                equal_set = compare.compare(l_forest[key].mid, r_forest[key].mid)
                Equal.extend(equal_set)

        type_mapping = ['Class', 'Struct', 'Union']

        if l_dataset_name == 'depends':
            if "TYPE" in l_forest.keys():
                for kind in type_mapping:
                    if kind in r_forest.keys():
                        compare = Tree.Compare()
                        equal_set = compare.compare(l_forest['TYPE'].mid, r_forest[kind].mid)
                        Equal.extend(equal_set)
        if r_dataset_name == 'depends':
            if "TYPE" in r_forest.keys():
                for kind in type_mapping:
                    if kind in l_forest.keys():
                        compare = Tree.Compare()
                        equal_set = compare.compare(l_forest[kind].mid, r_forest['TYPE'].mid)
                        Equal.extend(equal_set)

        logging.info(f"compare data costs: {datetime.now() - compare_start}.")
        return Equal

    def dependency_compare(self, l_dependency_data, r_dependency_data, l_mapping_dict, r_mapping_dict, l_dataset_name, r_dataset_name):
        edge_dict = dict()
        Equal_set = list()
        start = datetime.now()
        logging.info(f"start load {l_dataset_name} dependency data:")
        for index in range(0, len(l_dependency_data)):
            dep = l_dependency_data[index]
            if (dep['dependencySrcID'] in l_mapping_dict.keys()) & (dep['dependencyDestID'] in l_mapping_dict.keys()):
                # print(dep)
                dependency_kind = dep['dependencyType'].lower()
                if l_dataset_name == 'understand':
                    dependency_kind = self.resolveType(dependency_kind)
                if dependency_kind in self.dependency_map[l_dataset_name].keys():
                    dependency_kind = self.dependency_map[l_dataset_name][dependency_kind]
                    srcID = l_mapping_dict[dep['dependencySrcID']]
                    destID = l_mapping_dict[dep['dependencyDestID']]
                    if srcID not in edge_dict.keys():
                        edge_dict[srcID] = dict()
                    if destID not in edge_dict[srcID].keys():
                        edge_dict[srcID][destID] = list()
                    edge_dict[srcID][destID].append({'kind': dependency_kind, 'dataset': l_dataset_name, 'index': index})

        logging.info(f"load {l_dataset_name} dependency data costs: {datetime.now() - start}.")
        start = datetime.now()
        logging.info(f"start load {r_dataset_name} dependency data:")
        for index in range(0, len(r_dependency_data)):
            dep = r_dependency_data[index]
            if (dep['dependencySrcID'] in r_mapping_dict.keys()) & (dep['dependencyDestID'] in r_mapping_dict.keys()):
                # print(dep)
                dependency_kind = dep['dependencyType'].lower()
                if r_dataset_name == 'understand':
                    dependency_kind = self.resolveType(dependency_kind)
                if dependency_kind in self.dependency_map[r_dataset_name].keys():
                    dependency_kind = self.dependency_map[r_dataset_name][dependency_kind]
                    srcID = r_mapping_dict[dep['dependencySrcID']]
                    destID = r_mapping_dict[dep['dependencyDestID']]
                    if srcID not in edge_dict.keys():
                        edge_dict[srcID] = dict()
                    if destID not in edge_dict[srcID].keys():
                        edge_dict[srcID][destID] = list()
                    edge_dict[srcID][destID].append({'kind': dependency_kind, 'dataset': r_dataset_name, 'index': index})
        logging.info(f"load {r_dataset_name} dependency data costs: {datetime.now() - start}.")
        start = datetime.now()
        logging.info(f"deal with graph:")
        for node in edge_dict.keys():
            for neighbor in edge_dict[node].keys():
                equal_dep_index = dict()
                equal_dep_dataset = dict()
                if len(edge_dict[node][neighbor]) > 1:
                    for edge in edge_dict[node][neighbor]:
                        if edge['kind'] not in equal_dep_index.keys():
                            equal_dep_index[edge['kind']] = list()
                            equal_dep_dataset[edge['kind']] = list()
                        set_ = equal_dep_index[edge['kind']]
                        set_.append(edge['index'])
                        equal_dep_index[edge['kind']] = set_
                        set_ = equal_dep_dataset[edge['kind']]
                        set_.append(edge['dataset'])
                        equal_dep_dataset[edge['kind']] = set_
                    for key in equal_dep_index.keys():
                        if len(equal_dep_index[key]) > 1:
                            dep_equal = set(equal_dep_dataset[key])
                            l_set = set()
                            r_set = set()
                            if len(dep_equal) > 1:
                                for i in range(0, len(equal_dep_dataset[key])):
                                    if equal_dep_dataset[key][i] == l_dataset_name:
                                        l_set.add(equal_dep_index[key][i])
                                for i in range(0, len(equal_dep_dataset[key])):
                                    if equal_dep_dataset[key][i] == r_dataset_name:
                                        r_set.add(equal_dep_index[key][i])
                                Equal_set.append(tuple((l_set, r_set)))

        logging.info(f"compare data costs: {datetime.now() - start}.")
        return Equal_set

    def output(self, Equal_set: list, l_data, r_data, l_dataset_name, r_dataset_name, type):
        l_ne_set = set(range(len(l_data)))
        r_ne_set = set(range(len(r_data)))
        equal_result = list()
        for equal in Equal_set:
            equal_unit = dict()
            equal_unit["lgroup"] = list()
            equal_unit["rgroup"] = list()
            l_id = -1
            for id in equal[0]:
                if l_id == -1:
                    l_id = id
                entity = l_data[id]
                entity['dataset'] = l_dataset_name
                equal_unit["lgroup"].append(entity)
                if not id in l_ne_set:
                    logging.info(f"no this number in l_data {id}")
                else:
                    l_ne_set.remove(id)
            for id in equal[1]:
                entity = r_data[id]
                entity['dataset'] = r_dataset_name
                equal_unit["rgroup"].append(entity)
                if not id in r_ne_set:
                    logging.info(f"no this number in r_data {id}")
                else:
                    r_ne_set.remove(id)
            equal_result.append(equal_unit)

        ne_set = list()
        for id in l_ne_set:
            entity = l_data[id]
            entity['dataset'] = l_dataset_name
            ne_set.append(entity)
        for id in r_ne_set:
            entity = r_data[id]
            entity['dataset'] = r_dataset_name
            ne_set.append(entity)

        result_file = dict()
        result_file["eq_set"] = equal_result
        result_file['ne_set'] = ne_set

        result_str = json.dumps(result_file, indent=4)
        with open(f"./output_dir/{self.project_name}/{type}_{l_dataset_name}_{r_dataset_name}.json", 'w') as json_file:
            json_file.write(result_str)

    def get_equal_entity(self, entities):

        l_set = dict()
        r_set = dict()
        for entity_pair in entities:
            index = -1
            for l_entity in entity_pair['lgroup']:
                if index == -1:
                    index = l_entity['entityID']
                l_set[l_entity['entityID']] = index
            for r_entity in entity_pair['rgroup']:
                r_set[r_entity['entityID']] = index

        return l_set, r_set

    def entity_batch(self):
        tool_name = ['enre', 'understand', 'depends', 'sourcetrail']
        entity_data = dict()
        dependency_data = dict()
        for name in tool_name:
            entity_path = f"./input_dir/{self.project_name}/{name}_{self.project_name}_entity.json"
            entity_data[name] = self.load_entity_file(entity_path)
            self.build_trees(entity_data[name], name)
            dependency_path = f"./input_dir/{self.project_name}/{name}_{self.project_name}_dependency.json"
            dependency_data[name] = self.load_dependency_file(dependency_path)

        compare_pair = [['enre', 'understand'], ['enre', 'depends'], ['enre', 'sourcetrail'],
                        ['understand', 'depends'], ['understand', 'sourcetrail'], ['depends', 'sourcetrail']]

        Equal_set = [0, 0, 0, 0, 0, 0]
        for pair in compare_pair:
            logging.info(f"Start compare {pair[0]} and {pair[1]}...")
            index = compare_pair.index(pair)
            Equal_set[index] = self.entity_compare(pair[0], pair[1])
            self.output(Equal_set[index], entity_data[pair[0]], entity_data[pair[1]], pair[0], pair[1], 'entity')
            logging.info(f"{pair[0]} and {pair[1]} entity comparison finished")


    def dependency_batch(self):
        tool_name = ['enre', 'understand', 'depends', 'sourcetrail']
        dependency_data = dict()
        for name in tool_name:
            dependency_path = f"./input_dir/{self.project_name}/{name}_{self.project_name}_dependency.json"
            dependency_data[name] = self.load_dependency_file(dependency_path)

        compare_pair = [['enre', 'understand'], ['enre', 'depends'], ['enre', 'sourcetrail'],
                        ['understand', 'depends'], ['understand', 'sourcetrail'], ['depends', 'sourcetrail']]
        for pair in compare_pair:
            entity_result_path = f"./output_dir/{self.project_name}/entity_{pair[0]}_{pair[1]}.json"
            with open(entity_result_path, 'r') as file:
                data = json.load(file)
            l_set, r_set = self.get_equal_entity(data['eq_set'])
            logging.info(f"Start compare {pair[0]} and {pair[1]} dependency...")
            dependency_equal_set = self.dependency_compare(dependency_data[pair[0]], dependency_data[pair[1]], l_set, r_set, pair[0], pair[1])
            self.output(dependency_equal_set, dependency_data[pair[0]], dependency_data[pair[1]], pair[0], pair[1], 'dependency')
            logging.info(f"{pair[0]} and {pair[1]} dependency comparison finished")
