import re
import pandas as pd

# 读取.c文件的内容
path1 = 'example.c'

# 读取Excel文件
path2 = 'CANMatrix.xlsx'


def get_can_matrix_excel(file_path):
    df = pd.read_excel(file_path)

    # 创建一个字典来存储提取的信息
    signal_dict = {}

    # 处理每一行数据
    for index, row in df.iterrows():
        signal_name = row['信号名']
        id_name = row['报文ID']
        bit_range = row['Bit位']

        if pd.isna(id_name) or pd.isna(bit_range):
            exists = False
            start_bit = ''
            end_bit = ''
        else:
            exists = True
            bit_parts = bit_range.split('-')
            start_bit = bit_parts[0]
            end_bit = bit_parts[1] if len(bit_parts) > 1 else start_bit

        if pd.notna(id_name):
            id_name = id_name.replace('0x', '').replace('0X', '')

        # 构造字典的键
        key = f"{id_name}_{start_bit}_{end_bit}"

        # 将信息存储在字典中
        signal_dict[key] = {
            "信号名": signal_name,
            "ID名称": f"0x{id_name}" if pd.notna(id_name) else '',
            "起始位": start_bit,
            "结束位": end_bit,
            "是否存在": exists
        }

    # 打印字典内容
    for key, value in signal_dict.items():
        print(f"Key: {key}")
        for k, v in value.items():
            print(f"{k}: {v}")
        print("-" * 40)

    return signal_dict


def get_can_matrix_ch(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # 定义正则表达式模式
    pattern = re.compile(
        r'#define\s+(?P<signal_name>\w+)\s+(?i:0x)(?P<signal_address>\w+)\s*;\s*//(?i:0x)(?P<id>\w+),(?P<start_bit>[0-9\.]+)(?:-(?P<end_bit>[0-9\.]+))?,(?P<comment>[^;；\s]+)'
    )

    # 查找匹配的内容
    matches = pattern.finditer(data)

    # 创建一个字典来存储提取的信息
    signal_dict = {}

    # 处理匹配的内容
    for match in matches:
        signal_name = match.group('signal_name')
        signal_address = match.group('signal_address')
        id_name = match.group('id')
        start_bit = match.group('start_bit')
        end_bit = match.group('end_bit') if match.group('end_bit') else start_bit
        comment = match.group('comment').strip()

        # 构造字典的键
        key = f"{id_name}_{start_bit}_{end_bit}"

        # 将信息存储在字典中
        signal_dict[key] = {
            "信号名": signal_name,
            "信号地址": f"0x{signal_address}",
            "ID名称": f"0x{id_name}",
            "起始位": start_bit,
            "结束位": end_bit,
            "注释": comment
        }

    # 打印字典内容
    for key, value in signal_dict.items():
        print(f"Key: {key}")
        for k, v in value.items():
            print(f"{k}: {v}")
        print("-" * 40)

    return signal_dict



def compare_dicts(DictExcel, DictCH):
    # 创建一个新的字典来存储更新后的Dict1
    updated_Dict1 = {}
    
    for key, value in DictExcel.items():
        if value["是否存在"]:
            if key in DictCH:
                # 如果在Dict2中找到了相应的键
                updated_value = value.copy()
                updated_value["CanMap信号名称"] = DictCH[key]["信号名"]
                updated_value["CanMap信号是否存在"] = True
            else:
                # 如果在Dict2中没有找到相应的键
                updated_value = value.copy()
                updated_value["CanMap信号名称"] = None
                updated_value["CanMap信号是否存在"] = False
    
            updated_Dict1[key] = updated_value
    
    # 打印更新后的Dict1
    for key, value in updated_Dict1.items():
        print(f"Key: {key}")
        for k, v in value.items():
            print(f"{k}: {v}")
        print("-" * 40)

    return updated_Dict1


Dict2 = get_can_matrix_ch(path1)
Dict1 = get_can_matrix_excel(path2)
Dict = compare_dicts(Dict1, Dict2)

