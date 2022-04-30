import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

specifier_list = {
            'cpp': ['public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown', 'const', 'virtual', 'explicit', 'c ', 'default'],
            'java': ['java', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown'],
            'python': ['python', 'possible', 'public', 'private', 'protected', 'static', 'generic', 'abstract', 'unknown']
        }


def resolveEntityType(type: str, language) -> str:
    for specifier in specifier_list[language]:
        type = type.replace(specifier, "")
    type = type.strip()
    return type


def deal(project_name, dataset_l_name, dataset_r_name, type: str, language):
    path = "../output_dir/" + project_name + "/" + type +"_" + dataset_l_name + "_" + dataset_r_name + ".json"
    my_file = Path(path)
    if my_file.exists():
        print(path)
        if type == 'entity':
            eq_set, neq_set_l, neq_set_r = entity_deal(dataset_l_name, dataset_r_name, path, language)
            plot_show(eq_set, neq_set_l, neq_set_r)


def entity_deal(dataset_l_name, dataset_r_name, path, language):
    with open("../mappings/" + language + "_" + "map.json", 'r') as file:
        mapping = json.load(file)
    mapping = mapping['entity_map']
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    eq_set = dict()
    neq_set_l = dict()
    neq_set_r = dict()
    type = ""
    for eqs in data['eq_set']:
        for entity in eqs['lgroup']:
            type = entity['entityType'].lower()
            if entity['dataset'] == 'understand':
                type = resolveEntityType(type, language)
        mapped_type = mapping[dataset_l_name][type]
        if mapped_type not in eq_set.keys():
            eq_set[mapped_type] = 0
        eq_set[mapped_type] = eq_set[mapped_type] + max(len(eqs['lgroup']), len(eqs['rgroup']))

    for nes in data['ne_set']:
        type = nes['entityType'].lower()
        if nes['dataset'] == 'understand':
            type = resolveEntityType(type, language)
        mapped_type = mapping[nes['dataset']][type]
        if nes['dataset'] == dataset_l_name:
            if mapped_type not in neq_set_l.keys():
                neq_set_l[mapped_type] = 0
            neq_set_l[mapped_type] = neq_set_l[mapped_type] + 1
        if nes['dataset'] == dataset_r_name:
            if mapped_type not in neq_set_r.keys():
                neq_set_r[mapped_type] = 0
            neq_set_r[mapped_type] = neq_set_r[mapped_type] + 1

    print(eq_set, neq_set_l, neq_set_r)
    return eq_set, neq_set_l, neq_set_r


def dependency_deal(dataset_l_name, dataset_r_name, path):
    # equal_count_l, equal_count_r, not_equal_count_l, not_equal_count_r
    count = [0, 0, 0, 0]
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    for eqs in data['eq_set']:
        count[0] = count[0] + 1
        count[1] = count[1] + 1

    for nes in data['ne_set']:
        if nes['dataset'] == dataset_l_name:
            count[2] = count[2] + 1
        if nes['dataset'] == dataset_r_name:
            count[3] = count[3] + 1
    return count


def tool_review(raw_data, data_key, names, toolName, pic_number):
    r = range(0, len(names))
    df = pd.DataFrame(raw_data)

    # From raw value to percentage
    totals = [i + j + k for i, j, k in zip(df[data_key[0]], df[data_key[1]], df[data_key[2]])]
    equalBars = [i / j * 100 for i, j in zip(df[data_key[0]], totals)]
    lrBars = [i / j * 100 for i, j in zip(df[data_key[1]], totals)]
    rlBars = [i / j * 100 for i, j in zip(df[data_key[2]], totals)]

    barWidth = 0.85
    colors = plt.cm.Spectral(np.linspace(0.1, 0.4, 3))

    axs[pic_number].barh(r, equalBars, color=colors[0], edgecolor='white', height=barWidth, hatch='.',
                         label=data_key[0])
    axs[pic_number].barh(r, lrBars, left=equalBars, color=colors[1], edgecolor='white', height=barWidth, hatch='/',
                         label=data_key[1])
    axs[pic_number].barh(r, rlBars, left=[i + j for i, j in zip(equalBars, lrBars)], color=colors[2], edgecolor='white',
                         height=barWidth, hatch='\\', label=data_key[2])
    axs[pic_number].set_yticks(r, names)
    axs[pic_number].set_title(toolName)
    axs[pic_number].legend(loc='upper right')

def plot_show(eq_set, neq_set_l, neq_set_r):
    project_eq_count = []
    project_l_neq_count = []
    project_r_neq_count = []

    names = set(eq_set.keys()).union(set(neq_set_l.keys()))
    names = names.union(set(neq_set_r.keys()))
    names = list(names)

    for entity in names:
        if entity in eq_set.keys():
            project_eq_count.append(eq_set[entity])
        else:
            project_eq_count.append(0)
        if entity in neq_set_l.keys():
            project_l_neq_count.append(neq_set_l[entity])
        else:
            project_l_neq_count.append(0)
        if entity in neq_set_r.keys():
            project_r_neq_count.append(neq_set_r[entity])
        else:
            project_r_neq_count.append(0)

    raw_data = {'equal': project_eq_count,
                'l-r': project_l_neq_count,
                'r-l': project_r_neq_count}

    data_key = ['equal', 'l-r', 'r-l']
    tool_review(raw_data, data_key, names, dataset_l_name + "&" + dataset_r_name, i)


if __name__ == "__main__":
    data_l = ["depends", "enre", "enre", "enre", "understand", "understand"]
    data_r = ['sourcetrail', 'depends', 'sourcetrail', 'understand', 'depends', 'sourcetrail']
    fig, axs = plt.subplots(1, 6, figsize=(7, 15))  #

    project_list = ['halo', 'fastjson', 'mockito', 'MPAndroidChart', 'RxJava',  # 'pig', 'pdfbox', 'oozie', 'mall',
                    'bitcoin', 'calculator', 'leveldb', 'git', 'electron',
                    'boto3', 'glances', 'mypy', 'numpy']
    for project_name in project_list:
        for i in range(0, len(data_l)):
            dataset_l_name = data_l[i]  # "depends"
            dataset_r_name = data_r[i]
            print(dataset_l_name, "&", dataset_r_name)
            deal(project_name, dataset_l_name, dataset_r_name, "entity", "java")
            # deal(project_name, dataset_l_name, dataset_r_name, "dependency", "java")
        plt.show()

