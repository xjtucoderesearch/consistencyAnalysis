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

# Node declaration
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
    
# TODO: Modulize
def contain(keyword, raw):
    return bool(re.search(r'(^| )%s' % keyword, raw))


if __name__ == '__main__':
    print('Openning udb file...')
    db = understand.open(args.db)

    ent_list = []
    # # Add a default virtual file entity that holds all unresolved entities
    # ent_list.append({
    #     'id': 0,
    #     'type': 'File',
    #     'name': '[[Virtual File]]',
    # })

    # Extract file entities first
    print('Exporting File entities...')
    file_count = 0
    for ent in db.ents('File'):
        # Filter only java files
        if ent.language() == 'Java':
            ent_list.append(Entity(ent.id(),ent.longname(), 'File'));
            file_count += 1
    print(f'Total {file_count} files are successfully exported')

    print('Exporting entities other that File...')
    regular_count = 0

    # Package, not belonging to any real files, worth process separately
    for ent in db.ents('Package'):
        if ent.language() == 'Java':
            # Assign Packages to a virtual file to fulfill db schema
            ent_list.append(Entity(ent.id(),ent.longname(), ent.kindname()));
            regular_count += 1

    # Filter entities other than file
    for ent in db.ents('~File ~Package ~Unknown ~Unresolved ~Implicit'):
        if ent.language() == 'Java':
            # Although a suffix 's' is added, there should be only
            # one entry that matches the condition
            decls = ent.refs('Definein')
            if decls:
                # Normal entities should have a ref definein contains location
                # about where this entity is defined
                line = decls[0].line()
                start_column = decls[0].column() + 1
                end_column = start_column + len(ent.simplename())
                ent_list.append(Entity(ent.id(),ent.longname(), ent.kindname(), decls[0].file().longname(),
                line,  start_column, line, end_column));
                regular_count += 1
            else:
                print(
                    f'After {regular_count} successful append, an unseen situation occured')
                print(
                    ent.id(),
                    ent.kindname(),
                    ent.longname(),
                )
                all_ref_kinds = set()
                for ref in ent.refs():
                    all_ref_kinds.add(ref.kind().longname())
                print('All possible ref kinds are', all_ref_kinds)

                sys.exit(-1)

    print('Saving results to the file...')
    entity_file = dict()
    entity_file["schemaVersion"] = 1.0
    entity_file['entity'] = ent_list
    entity_file['projectName'] = args.projectname
    entity_str = json.dumps(entity_file, indent=4)
    with open(args.out, 'w') as json_file:
        json_file.write(entity_str)