import yaml
file_path = "src/file_config.yaml"
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        file_config = yaml.safe_load(f)
except Exception as e:
    raise e
