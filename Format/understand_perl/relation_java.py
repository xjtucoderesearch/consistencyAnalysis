import understand
import argparse
import json
import sys
import re

# Usage
parser = argparse.ArgumentParser()
parser.add_argument('db', help='Specify Understand database')
parser.add_argument('out', help='specify output file\'s name and location')
parser.add_argument('projectname', help='the name of project')
args = parser.parse_args()


def contain(keyword, raw):
    return bool(re.search(r'(^| )%s' % keyword, raw))


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


if __name__ == '__main__':
    print('Openning udb file...')
    db = understand.open(args.db)

    rel_list = []

    print('Exporting relations...')
    rel_count = 0
    for ent in db.ents():
        if ent.language() == 'Java':
            for ref in ent.refs('~End', '~Unknown ~Unresolved ~Implicit'):
                if ref.isforward():
                    rel_list.append(Dependency(ref.kind().longname(), ref.scope().id(), ref.ent().id(), ref.line(), ref.column(), ref.line(), ref.column()))
                    rel_count += 1

    all_rel_kinds = set()

    print('Saving results to the file...')
    dependency_file = dict()
    dependency_file["schemaVersion"] = 1.0
    dependency_file['dependency'] = rel_list
    dependency_file['projectName'] = args.projectname
    dependency_str = json.dumps(dependency_file, indent=4)
    with open(args.out, 'w') as json_file:
        json_file.write(dependency_str)
    print(f'Total {rel_count} relations are successfully exported')