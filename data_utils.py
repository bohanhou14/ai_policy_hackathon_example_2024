import json

def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def write_jsonl(file_path, data):
    with open(file_path, 'w') as f:
        for line in data:
            f.write(json.dumps(line, default=str))
            f.write("\n")