# 读取原始 CSV 文件
import pandas as pd
import re

# 文件路径
input_file = 'Filtered_GamingBook.csv'  # 输入文件路径
output_file = 'Processed_GamingBook.csv'  # 输出文件路径
# input_file = 'Filtered_Ultrabook.csv'
# output_file = 'Processed_Ultrabook.csv'

# 加载 CSV 文件
df = pd.read_csv(input_file, encoding='utf-8-sig')

# 筛选上市时间为2023或2024年的数据
if '上市时间' in df.columns:
    df = df[df['上市时间'].astype(str).str.startswith(('2024', '2023'))]

# 定义处理空值的函数
def fill_missing_values(row):
    for col in row.index:
        if pd.isnull(row[col]):
            row[col] = f"Unknown {col}"  # 填充格式为“Unknown + 列名”
    return row

# 对每一行应用空值填充函数
df = df.apply(fill_missing_values, axis=1)

def extract_screen_size(value):
    """
    提取屏幕尺寸中的数字部分。
    如果值以 'Unknown' 开头，保持原样。
    """
    if isinstance(value, str):  # 确保值是字符串
        if value.startswith("Unknown"):
            return value  # 保持原样
        match = re.search(r"(\d+\.?\d*)英寸", value)  # 匹配带有'英寸'的数字
        if match:
            return float(match.group(1))  # 提取匹配的数字并转为浮点数
    return value  # 返回原值（如NaN或其他未匹配情况）

# 对屏幕尺寸列进行处理
df["屏幕尺寸"] = df["屏幕尺寸"].apply(extract_screen_size)

# 预处理屏幕刷新率列，提取其中的数字部分
def extract_refresh_rate(value):
    """
    提取屏幕刷新率中的数字部分，去掉 Hz。
    如果值以 'Unknown' 开头或为空，保持原样。
    """
    if isinstance(value, str):
        if value.startswith("Unknown"):
            return value
        match = re.search(r"(\d+)", value)  # 匹配纯数字部分
        if match:
            return int(match.group(1))  # 返回整数形式的刷新率
    return value

# 对屏幕刷新率列进行处理
df["屏幕刷新率"] = df["屏幕刷新率"].apply(extract_refresh_rate)

# 预处理笔记本重量列，提取其中的数字部分
def extract_weight(value):
    """
    提取笔记本重量中的数字部分，去掉 Kg 单位。
    如果值无效或以 'Unknown' 开头，保持原样。
    """
    if isinstance(value, str):
        if value.startswith("Unknown"):
            return value
        match = re.search(r"(\d+\.?\d*)", value)  # 匹配浮点数或整数部分
        if match:
            return float(match.group(1))  # 返回浮点数形式的重量
    return value

# 对笔记本重量列进行处理
df["笔记本重量"] = df["笔记本重量"].apply(extract_weight)

# 预处理内存容量列，提取其中的数字部分
def extract_memory_capacity(value):
    """
    提取内存容量中的数字部分，去掉 GB 单位。
    如果值无效或以 'Unknown' 开头，保持原样。
    """
    if isinstance(value, str):
        if value.startswith("Unknown"):
            return value
        match = re.search(r"(\d+)", value)  # 匹配纯数字部分
        if match:
            return int(match.group(1))  # 返回整数形式的内存容量
    return value

# 对内存容量列进行处理
df["内存容量"] = df["内存容量"].apply(extract_memory_capacity)

# 根据参考报价生成价格区间
def get_price_range(price):
    if pd.isnull(price):
        return "Unknown"
    try:
        price = float(price)
        if 1000 <= price < 2000:
            return "1000-2000"
        elif 2000 <= price < 3000:
            return "2000-3000"
        elif 3000 <= price < 4000:
            return "3000-4000"
        elif 4000 <= price < 5000:
            return "4000-5000"
        elif 5000 <= price < 6000:
            return "5000-6000"
        elif 6000 <= price < 7000:
            return "6000-7000"
        elif 7000 <= price < 8000:
            return "7000-8000"
        elif 8000 <= price < 9000:
            return "8000-9000"
        elif 9000 <= price < 10000:
            return "9000-10000"
        else:
            return "10000以上"
    except ValueError:
        return "Unknown"

# 应用价格区间生成函数
df['价格区间'] = df['参考报价'].apply(get_price_range)

# 替换“英特尔”为“Intel”
df.replace({"英特尔": "Intel"}, regex=True, inplace=True)

# 删除 CPU型号 列中从“高端机”/“旗舰机”/“中端主流机”之后的内容
def clean_cpu_model(cpu_model):
    if pd.isnull(cpu_model):
        return cpu_model
    # 找到关键词的位置并裁剪字符串
    for keyword in ["高端机", "旗舰机", "中端主流机"]:
        if keyword in cpu_model:
            return cpu_model.split(keyword)[0].strip()
    return cpu_model

# 应用 CPU 型号清理函数
df['CPU型号'] = df['CPU型号'].apply(clean_cpu_model)

# 根据文件名统一产品定位
if "GamingBook" in input_file:
    df['产品定位'] = "游戏本"
elif "Ultrabook" in input_file:
    df['产品定位'] = "轻薄本"

# 将处理后的数据保存为新的 CSV 文件
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"处理后的数据已保存为 {output_file}")
