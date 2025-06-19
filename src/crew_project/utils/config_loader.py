import yaml
from pathlib import Path

def load_yaml_config(path: str) -> dict:
    with open(Path(__file__).parent.parent / path, 'r') as f:
        return yaml.safe_load(f) 