import subprocess
import argparse
from os import path
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from Format.Depends import depends
from Format.ENRE import enre
from Format.Sourcetrail import sourcetrail
from Format.Understand import understand

def ENRE_batch(lang, project_name, dir):
    # Run ENRE
    print('Starting ENRE')
    if lang == 'java':
        cmd = f'java -jar {path.join(path.dirname(__file__), r"./tools/enre/enre-java.jar")} java {dir} {project_name}'
    elif lang == 'cpp':
        cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/enre/enre-cpp.jar")} cpp {dir} {project_name} {project_name}'
    else:
        cmd = f'{path.join(path.dirname(__file__), "./tools/enre/enre-python.exe")} {dir}'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=f'./out/enre-{lang}')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)
    # Format ENRE
    if lang == 'cpp':
        input_path = f'./out/enre-{lang}/{project_name}'
    elif lang == 'java':
        input_path = f'./out/enre-{lang}/{project_name}-enre-out/{project_name}-out.json'
    else:
        input_path = f'./out/enre-{lang}/{project_name}-report-enre.json'
    enre(lang, project_name, input_path, f'./out/enre-{lang}/')


def Depends_batch(lang, project_name, dir):
    # Run Depends
    print('starting Depends')
    cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/depends.jar")} {lang} {dir} {project_name}'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./out/depends')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)
    depends(f'./out/depends/{project_name}.json', project_name, f'./out/depends/', '', lang)

def Undertstand_batch(lang, project_name, dir):
    # Run Understand
    print('Starting Understand')
    upath = f'./out/understand/{project_name}.und'
    if lang == 'cpp':
        ulang = 'C++'
    elif lang == 'java':
        ulang = 'Java'
    else:
        ulang = 'Python'
    cmd = f'und create -db {upath} -languages {ulang} add {dir} analyze -all'

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./out/understand')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)

    cmd = f'upython {path.join(path.dirname(__file__), f"./Format/understand_perl/entity_{lang}.py")} ' \
          f'{upath} {project_name}_entity.json {project_name}'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./out/understand')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)
    cmd = f'upython {path.join(path.dirname(__file__), f"./Format/understand_perl/relation_{lang}.py")} ' \
          f'{upath} {project_name}_dependency.json {project_name}'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./out/understand')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)
    understand(f'./out/understand/{project_name}_entity.json', './out/understand', project_name)


def Sourcetrail_batch(lang, project_name, dir):
    # Run SourceTrail
    print('Start SourceTrail')
    spath = f'./out/sourcetrail/{project_name}/{project_name}.srctrlprj'
    if path.exists(spath):
        cmd = f'sourcetrail index --project-file {path.join(path.dirname(__file__), spath)}'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='./out/sourcetrail')
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        print(line)
    db_path = f'./out/sourcetrail/{project_name}/{project_name}.srctrldb'
    sourcetrail(project_name, lang, db_path, f'./out/sourcetrail/')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lang", help='Sepcify the target language')
    parser.add_argument("dir", help='Specify the root of the project to analysis')
    args = parser.parse_args()

    lang = args.lang
    dir = args.dir
    project_name = dir.split("\\")[-1]
    ENRE_batch(lang, project_name, dir)
    Undertstand_batch(lang, project_name, dir)
    Depends_batch(lang, project_name, dir)
    Sourcetrail_batch(lang, project_name, dir)




