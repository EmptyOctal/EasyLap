from neo4j import GraphDatabase
import pandas as pd

# 加载CSV数据
cpu_file = 'dataset\\laptop\\Processed_CPU_info.csv'  # CSV 文件路径
# input_file = 'dataset\\laptop\\Processed_GamingBook.csv'  # CSV文件路径
input_file = 'dataset\\laptop\\Processed_Ultrabook.csv'
df = pd.read_csv(input_file)
cpu_df = pd.read_csv(cpu_file)

# 连接到Neo4j数据库
uri = "bolt://localhost:7687"  # Neo4j 连接地址
username = "neo4j"  # Neo4j 用户名
password = "12345678"  # Neo4j 密码
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_product_nodes(tx, product):
    # 创建产品节点
    tx.run("""
    MERGE (p:Product {name: $name, link: $link, image: $image, price: $price, 
                      battery_life: $battery_life, weight: $weight, touch_screen: $touch_screen,
                      shell_description: $shell_description, shell_material: $shell_material, 
                      keyboard_description: $keyboard_description, screen_resolution: $screen_resolution, 
                      screen_refresh_rate: $screen_refresh_rate, screen_size: $screen_size, 
                      data_ports: $data_ports, release_date: $release_date})
    """, 
    name=product['产品名称'], 
    link=product['链接'],
    image=product['图片链接'],
    price=product['参考报价'],
    battery_life=product['续航时间'],
    weight=product['笔记本重量'],
    touch_screen=product['触控屏'],
    shell_description=product['外壳描述'],
    shell_material=product['外壳材质'],
    keyboard_description=product['键盘描述'],
    screen_resolution=product['屏幕分辨率'],
    screen_refresh_rate=product['屏幕刷新率'],
    screen_size=product['屏幕尺寸'],
    data_ports=product['数据接口'],
    release_date=product['上市时间'])

def create_cpu_node(tx, cpu_model):
    # 创建 CPU 节点（只创建节点，不包含属性）
    tx.run("""
    MERGE (c:CPU {model: $model})
    """, model=cpu_model)

def update_cpu_node_with_attributes(tx, cpu_model, cpu_info):
    # 更新CPU节点的属性
    tx.run("""
    MATCH (c:CPU {model: $model})
    SET c.rank = $rank,
        c.base_clock = $base_clock,
        c.series = $series,
        c.process = $process,
        c.boost_clock = $boost_clock,
        c.socket_type = $socket_type,
        c.core_thread = $core_thread,
        c.core_code = $core_code,
        c.tdp = $tdp,
        c.integrated_graphics = $integrated_graphics
    """, 
    model=cpu_model,
    rank=cpu_info['综合排名'],
    base_clock=cpu_info['CPU主频'],
    series=cpu_info['CPU系列'],
    process=cpu_info['制作工艺'],
    boost_clock=cpu_info['加速频率'],
    socket_type=cpu_info['插槽类型'],
    core_thread=cpu_info['核心/线程'],
    core_code=cpu_info['核心代号'],
    tdp=cpu_info['热设计功耗'],
    integrated_graphics=cpu_info['集成显卡'])

def create_gpu_node(tx, gpu):
    # 创建 GPU 节点
    tx.run("MERGE (g:GPU {model: $gpu})", gpu=gpu)

def create_category_node(tx, category):
    # 创建产品定位节点
    tx.run("MERGE (cat:ProductCategory {name: $category})", category=category)

def create_price_range_node(tx, price_range):
    # 创建价格区间节点
    tx.run("MERGE (pr:PriceRange {range: $price_range})", price_range=price_range)

def create_relationships(tx, product_name, cpu, gpu, category, price_range):
    # 创建产品与其他节点之间的关系
    tx.run("""
    MATCH (p:Product {name: $product_name}), 
          (c:CPU {model: $cpu}), 
          (g:GPU {model: $gpu}), 
          (cat:ProductCategory {name: $category}), 
          (pr:PriceRange {range: $price_range})
    MERGE (p)-[:HAS_CPU]->(c)
    MERGE (p)-[:HAS_GPU]->(g)
    MERGE (p)-[:BELONGS_TO]->(cat)
    MERGE (p)-[:IN_PRICE_RANGE]->(pr)
    """, 
    product_name=product_name, 
    cpu=cpu, 
    gpu=gpu, 
    category=category, 
    price_range=price_range)

# 创建产品节点、CPU节点和关系
with driver.session() as session:
    for _, product in df.iterrows():
        session.execute_write(create_product_nodes, product)
        session.execute_write(create_gpu_node, product['显卡芯片'])
        session.execute_write(create_category_node, product['产品定位'])
        session.execute_write(create_price_range_node, product['价格区间'])
        
        # 创建 CPU 节点，如果该 CPU 尚不存在
        session.execute_write(create_cpu_node, product['CPU型号'])
        
        # 确保找到匹配的 CPU 信息
        cpu_info = cpu_df[cpu_df['CPU型号'] == product['CPU型号']]
        
        if not cpu_info.empty:  # 如果找到了对应的 CPU 信息
            session.execute_write(update_cpu_node_with_attributes, product['CPU型号'], cpu_info.iloc[0])
        else:
            print(f"Warning: No CPU information found for product {product['产品名称']} with CPU型号 {product['CPU型号']}")
        
        # 创建关系
        session.execute_write(create_relationships, product['产品名称'], product['CPU型号'], 
                              product['显卡芯片'], product['产品定位'], product['价格区间'])

# 关闭连接
driver.close()
