import os
from openai import OpenAI

try:
    # 使用OpenAI兼容模式调用通义千问
    client = OpenAI(
        api_key="sk-5f4560219d2946bc8a499184979151cf",  # 从环境变量读取API Key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里云OpenAI兼容接口地址
    )

    # 调用聊天接口
    completion = client.chat.completions.create(
        model="qwen-plus",  # 指定通义千问模型
        messages=[
            {'role': 'system', 'content': "你是一位关系抽取专家，擅长从文本中提取实体和关系。如果您不知道要求提取的属性值，则为属性值返回null。已知候选的关系列表:['优点','缺点']，从以下输入中抽取可能存在的头实体和尾实体并以['头实体','关系','尾实体']的格式返回给我"},
            {'role': 'user', 'content': '机械革命极光X：首发价6499的4070，性价比很高。散热风扇的噪音控制得很好。如果忽略机械革命的品控问题的话的确不错。我到手的这款屏幕有一个坏点'}
        ]
    )
    # 输出模型回复
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"错误信息：{e}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
