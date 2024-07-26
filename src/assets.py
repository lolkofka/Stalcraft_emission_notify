import json
import os.path

if not os.path.exists('data'):
    os.mkdir('data')

with open('assets/default_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
