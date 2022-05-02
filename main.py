from datetime import datetime
from Batch import Batch
import logging

if __name__ == '__main__':
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                f'./logs/{timestamp}.log'),
            logging.StreamHandler()
        ]
    )


    language = "cpp"
    cpp_project = ["bitcoin", "electron", "leveldb", "calculator", "git"]
    for project in cpp_project:
        logging.info(f"start analysis {project}")
        start = datetime.now()
        batch = Batch(language, project, "::")
        batch.entity_batch()
        batch.dependency_batch()
        logging.info(f"analysis {project} costs: {datetime.now() - start}.")

    language = "java"
    java_project = ['halo', 'fastjson', 'mockito', 'MPAndroidChart', 'RxJava']
    for project in java_project:
        logging.info(f"start analysis {project}")
        start = datetime.now()
        batch = Batch(language, project, ".")
        batch.entity_batch()
        batch.dependency_batch()
        logging.info(f"analysis {project} costs: {datetime.now() - start}.")

    language = "python"
    java_project = ['keras','boto3', 'glances',  'mypy', 'numpy']
    for project in java_project:
        logging.info(f"start analysis {project}")
        start = datetime.now()
        batch = Batch(language, project, ".")
        batch.entity_batch()
        batch.dependency_batch()
        logging.info(f"analysis {project} costs: {datetime.now() - start}.")



