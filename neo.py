# 导入函数
def parse_model_output(model_output):
    conditions = {}
    try:
        for item in model_output.split(","):
            key, value = item.split(":")
            conditions[key.strip()] = value.strip()
    except Exception as e:
        print(f"解析错误: {e}")
        return {"error": "解析模型输出失败"}
    return conditions


def map_conditions_to_query(conditions):
    query_conditions = {"where_clauses": [], "params": {}}

    # 使用场景 → 产品定位
    if "使用场景" in conditions:
        if conditions["使用场景"] in ["游戏", "编程", "影视后期"]:
            query_conditions["where_clauses"].append("p.category = $category")
            query_conditions["params"]["category"] = "游戏本"
        else:
            query_conditions["where_clauses"].append("p.category = $category")
            query_conditions["params"]["category"] = "轻薄本"

    # 预算 → 价格区间
    if "预算" in conditions:
        query_conditions["where_clauses"].append("p.price CONTAINS $budget")
        query_conditions["params"]["budget"] = conditions["预算"]

    # 便携性 → 笔记本重量
    if "便携性" in conditions and conditions["便携性"] == "便携":
        query_conditions["where_clauses"].append("p.weight < 2")

    # CPU偏好 → CPU型号
    if "CPU偏好" in conditions:
        if conditions["CPU偏好"] == "Intel系列":
            query_conditions["where_clauses"].append("c.model STARTS WITH 'Intel'")
        elif conditions["CPU偏好"] == "AMD系列":
            query_conditions["where_clauses"].append("c.model STARTS WITH 'AMD'")

    # 性能需求 → GPU型号
    if "性能需求" in conditions:
        if conditions["性能需求"] == "极高性能":
            query_conditions["where_clauses"].append("g.model CONTAINS '4070' OR g.model CONTAINS '4080' OR g.model CONTAINS '4090'")
        elif conditions["性能需求"] == "高性能":
            query_conditions["where_clauses"].append("g.model CONTAINS '3050' OR g.model CONTAINS '4050' OR g.model CONTAINS '4060'")
        else:
            query_conditions["where_clauses"].append("NOT (g.model CONTAINS '4070' OR g.model CONTAINS '4080' OR g.model CONTAINS '4090')")

    # 屏幕尺寸
    if "屏幕尺寸偏好" in conditions:
        if conditions["屏幕尺寸偏好"] == "较小":
            query_conditions["where_clauses"].append("p.screen_size < 15")
        elif conditions["屏幕尺寸偏好"] == "中等":
            query_conditions["where_clauses"].append("p.screen_size < 16")
        elif conditions["屏幕尺寸偏好"] == "较大":
            query_conditions["where_clauses"].append("p.screen_size >= 16")

    # 屏幕刷新率
    if "屏幕刷新率偏好" in conditions and conditions["屏幕刷新率偏好"] == "刷新率较高":
        query_conditions["where_clauses"].append("p.screen_refresh_rate >= 144")

    # 内存需求
    if "内存容量偏好" in conditions and conditions["内存容量偏好"] == "较大":
        query_conditions["where_clauses"].append("p.memory >= 32")

    return query_conditions


def build_cypher_query(mapped_conditions):
    """
    根据新的关系生成正确的 Cypher 查询。
    """
    # 基础查询，假设所有关系指向产品节点
    base_query = """
    MATCH (p:Product)
    """

    # 根据条件添加不同的 WHERE 子句
    for clause in mapped_conditions["where_clauses"]:
        base_query += f" OR {clause}"

    # 返回产品节点的属性及相关GPU信息
    base_query += """
    RETURN p.name AS title, p.link AS link, p.image AS image, p.price AS price, 
           p.weight AS weight, c.model AS cpu, p.memory AS memory, p.disk AS disk, 
           g.model AS gpu, p.size AS size, p.ReleaseDate AS ReleaseDate 
    LIMIT 5
    """

    return base_query, mapped_conditions["params"]

# 测试函数
if __name__ == "__main__":
    # 输入测试文本
    test_output = "使用场景: 游戏, 预算: 5000-6000, 便携性: 无, CPU偏好: Intel系列, 性能需求: 高性能, 屏幕尺寸偏好: 较大, 屏幕刷新率偏好: 刷新率较高, 内存容量偏好: 较大"

    print("======== 测试 parse_model_output ========")
    conditions = parse_model_output(test_output)
    print("解析结果:", conditions)

    print("\n======== 测试 map_conditions_to_query ========")
    mapped_query = map_conditions_to_query(conditions)
    print("生成的查询条件:", mapped_query)

    print("\n======== 测试 build_cypher_query ========")
    cypher_query, params = build_cypher_query(mapped_query)
    print("生成的Cypher查询语句:")
    print(cypher_query)
    print("查询参数:", params)
