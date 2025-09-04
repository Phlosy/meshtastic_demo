import yaml

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

