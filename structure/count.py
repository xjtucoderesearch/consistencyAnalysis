import csv
import json

class count:
    def __init__(self, mapping, language, project_name):
        self.mapping = mapping
        self.language = language
        self.project_name = project_name
        self.specifier_list = {
            'cpp': ['public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown', 'const', 'virtual',
                'explicit', 'c ', 'default'],
            'java': ['java', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown'],
            'python': ['python', 'possible', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown']
        }
        self.data_count = dict()

    def batch(self):
        compare_pair = [['enre', 'understand'], ['enre', 'depends'], ['enre', 'sourcetrail'],
                        ['understand', 'depends'], ['understand', 'sourcetrail'], ['depends', 'sourcetrail']]
        for pair in compare_pair:
            path = "../output_dir/" + project_name + "/entity_" + pair[0] + "_" + pair[1] + ".json"
            self.data_count[pair[0] + "&" + pair[1]] = self.entity(path, pair[0], pair[1])
        self.output()

    def resolve(self, type, dataset_name):
        type = type.lower()

        if dataset_name == 'understand':
            for specifier in self.specifier_list[language]:
                type = type.replace(specifier, "")
                type = type.strip()
        if type in self.mapping['entity_map'][dataset_name].keys():
            type = self.mapping['entity_map'][dataset_name][type]
        return type

    def entity(self, path:str, l_dataset_name, r_dataset_name):
        with open(path, 'r') as file:
            data = json.load(file)
        l_equal_count = dict()
        r_equal_count = dict()
        for pair in data['eq_set']:
            type = self.resolve(pair['lgroup'][0]['entityType'], l_dataset_name)
            if type not in l_equal_count.keys():
                l_equal_count[type] = 0
                r_equal_count[type] = 0
            l_equal_count[type] = l_equal_count[type] + len(pair['lgroup'])
            r_equal_count[type] = r_equal_count[type] + len(pair['rgroup'])
        l_sum = sum([l_equal_count[key] for key in l_equal_count.keys()])
        l_equal_count['sum'] = l_sum
        r_sum = sum([r_equal_count[key] for key in r_equal_count.keys()])
        r_equal_count['sum'] = r_sum
        print(l_equal_count)
        print(r_equal_count)

        l_not_equal_count = dict()
        r_not_equal_count = dict()
        for entity in data['ne_set']:
            if entity['dataset'] == l_dataset_name:
                type = self.resolve(entity['entityType'], l_dataset_name)
                if type not in l_not_equal_count.keys():
                    l_not_equal_count[type] = 0
                l_not_equal_count[type] = l_not_equal_count[type] + 1
            if entity['dataset'] == r_dataset_name:
                type = self.resolve(entity['entityType'], r_dataset_name)
                if type not in r_not_equal_count.keys():
                    r_not_equal_count[type] = 0
                r_not_equal_count[type] = r_not_equal_count[type] + 1
        l_sum = sum([l_not_equal_count[key] for key in l_not_equal_count.keys()])
        l_not_equal_count['sum'] = l_sum
        r_sum = sum([r_not_equal_count[key] for key in r_not_equal_count.keys()])
        r_not_equal_count['sum'] = r_sum

        print(l_not_equal_count)
        print(r_not_equal_count)

        Jaccard_index = dict()
        for kind in l_equal_count.keys():
            if kind not in l_not_equal_count.keys():
                l = 0
            else:
                l = l_not_equal_count[kind]
            if kind not in r_not_equal_count.keys():
                r = 0
            else:
                r = r_not_equal_count[kind]
            equal_count = (l_equal_count[kind] + r_equal_count[kind])/2
            Jaccard_index[kind] = equal_count / (l + r + equal_count)
        print(Jaccard_index)
        return {
            'l_equal': l_equal_count,
            'r_equal': r_equal_count,
            'l_ne': l_not_equal_count,
            'r_ne': r_not_equal_count,
            'Jaccard': Jaccard_index
        }

    def output(self):
        data_count = self.data_count
        with open('../count_file/{}.csv'.format(project_name), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            for key in data_count.keys():
                l_dataset_name = key.split("&")[0]
                r_dataset_name = key.split("&")[1]
                l_equal_count = data_count[key]['l_equal']
                r_equal_count = data_count[key]['r_equal']
                l_not_equal_count = data_count[key]['l_ne']
                r_not_equal_count = data_count[key]['r_ne']
                Jaccard_index = data_count[key]['Jaccard']

                writer.writerow([l_dataset_name + "&" + r_dataset_name])
                writer.writerow(l_equal_count.keys())
                writer.writerow([l_equal_count[key] for key in l_equal_count.keys()])
                writer.writerow(r_equal_count.keys())
                writer.writerow([r_equal_count[key] for key in r_equal_count.keys()])
                writer.writerow(l_not_equal_count.keys())
                writer.writerow([l_not_equal_count[key] for key in l_not_equal_count.keys()])
                writer.writerow(r_not_equal_count.keys())
                writer.writerow([r_not_equal_count[key] for key in r_not_equal_count.keys()])
                writer.writerow(Jaccard_index.keys())
                writer.writerow([Jaccard_index[key] for key in Jaccard_index.keys()])


if __name__ == "__main__":
    project_list = ['halo', 'fastjson', 'mockito', 'MPAndroidChart', 'RxJava',
                    'bitcoin', 'calculator', 'leveldb', 'git', 'electron',
                    'boto3', 'glances', 'mypy', 'numpy', 'keras']
    language_list = ['java', 'java', 'java', 'java', 'java',
                     'cpp', 'cpp', 'cpp', 'cpp', 'cpp',
                     'python', 'python', 'python', 'python', 'python']

    for i in range(0, len(project_list)):
        project_name = project_list[i]
        language = language_list[i]
        mapping_path = "../mappings/" + language + "_map.json"
        with open(mapping_path, 'r') as file:
            mapping = json.load(file)
        entity_count = count(mapping, language, project_name)
        entity_count.batch()

