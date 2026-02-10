import json

def get_data(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(data)
    return data