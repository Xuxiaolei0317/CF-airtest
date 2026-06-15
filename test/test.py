import json

# 定义 JSON 文件路径
file_path = './config.json'

try:
    # 打开并读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(data)

except FileNotFoundError:
    print(f"未找到文件 {file_path}")
except json.JSONDecodeError:
    print(f"解析 {file_path} 时出错，请检查 JSON 格式")