import json

# 定义节点信息字符串
node_info_str = """
Path from root node: [0, 2, 0]
Payload details:
	  type :  Button 
	  name :  Button 
	  text :   
	  desc :  Button 
	  tag :  -1 
	  enabled :  True 
	  visible :  True 
	  zOrders :  {'local': 0, 'global': 0} 
	  anchorPoint :  [0.5, 0.5] 
	  size :  [0.0325, 0.068055555555556] 
	  scale :  [1, 1] 
	  pos :  [0.03125, 0.79166666666667] 
	  skew :  [0, 0] 
	  rotation :  0 
	  touchable :  True 
	  rotation3D :  {'y': 0, 'z': 0, 'x': 0} 
"""

# 解析节点信息
node_info = {}
lines = node_info_str.strip().split('\n')
path_line = lines[0]
path = eval(path_line.split(': ')[1])
node_info['path'] = path

for line in lines[2:]:
    if line.strip():
        key, value = line.split(' : ', 1)
        try:
            # 尝试将值转换为合适的 Python 类型
            node_info[key.strip()] = eval(value.strip())
        except:
            node_info[key.strip()] = value.strip()

# 读取 config.json 文件
config_file_path = '/Users/xxl/CF_Airtest/config.json'
try:
    with open(config_file_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
except FileNotFoundError:
    config_data = {}
except json.JSONDecodeError:
    config_data = {}

# 将节点信息添加到 config 中，假设添加到一个名为 sprites 的列表里
if 'sprites' not in config_data:
    config_data['sprites'] = []
config_data['sprites'].append(node_info)

# 将更新后的数据写回到 config.json 文件
with open(config_file_path, 'w', encoding='utf-8') as file:
    json.dump(config_data, file, indent=4)

print("节点信息已成功导入到 config.json 文件中。")
