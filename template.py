import os
from pathlib import Path
import logging

list_of_files = [
    ".github/workflows/.gitkeep",
    "components/__init__.py",

    "utils/__init__.py",
    "utils/common.py",

    "config/__init__.py",
    "config/configuration.py",

    "knowledge/__init__.py",

    "pipeline/__init__.py",
    "pipeline/input/__init__.py",
    "pipeline/asr/__init__.py",
    "pipeline/retrieval/__init__.py",
    "pipeline/llm/__init__.py",
    "pipeline/tts/__init__.py",
    "pipeline/a2f/__init__.py",
    "pipeline/a2m/__init__.py",
    "pipeline/output/__init__.py",

    "entity/__init__.py",
    "entity/config_entity.py",

    "constants/__init__.py",

    "models/__init__.py",

    "logs/__init__.py",

    "diagrams/__init__.py",

    "monitoring/prometheus.yml",
    "monitoring/grafana_dashboard.yml",

    "research/research.ipynb",

    "config/config.yaml",
    "params.yaml",
    "schema.yaml",
    "main.py",
    "requirements.txt",
    "setup.py",
    "templates/index.html"
]

for file_path in list_of_files:
    file_path = Path(file_path)
    file_dir, file_name = os.path.split(file_path)

    if file_dir != "":
        os.makedirs(file_dir, exist_ok=True)
        logging.info(f"Creating directory:{file_dir} for the file {file_name}")

    if (not os.path.exists(file_path)) or (os.path.getsize(file_path) == 0):
        with open(file_path, 'w') as f:
            logging.info(f"Creating empty file: {file_path}")
    else:
        logging.info(f"{file_name} is~ already exists")