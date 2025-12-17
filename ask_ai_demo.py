import requests
import json
import os

api_key = os.getenv("api_key", "yourkey") # 可以在平台申请 https://platform.xiaomimimo.com/#/console/api-keys
base_url = os.getenv("base_url", "https://api.xiaomimimo.com/v1/chat/completions")
model = os.path.join("model", "mimo-v2-flash")


def parse_response(raw_json):
    print(raw_json)
    outer_data = json.loads(raw_json)
    content_str = outer_data["choices"][0]["message"]["content"]
    pure_json_str = content_str.strip().strip("```json").strip("```").strip()
    result_dict = json.loads(pure_json_str)
    return result_dict


# 加载ai模型
def load_ai_ask(prompt, text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        # "model": "inclusionAI/Ling-1T",
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": text},
        ],
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
        "temperature": 0.8,
    }
    max_retries = 4  # 最大重试次数
    retry_count = 0  # 当前重试计数

    while retry_count < max_retries:
        try:
            response = requests.post(base_url, headers=headers, data=json.dumps(data))
            return parse_response(response.text)
        except Exception as e:
            retry_count += 1
            print(f"第{retry_count}次尝试失败：{e}")
            # 如果达到最大重试次数，返回错误信息
            if retry_count == max_retries:
                return f"已达到最大重试次数（{max_retries}次），操作失败"
    return None


system_prompt = """
请忽略之前的对话,我想让你做我的好朋友，你现在会扮演我的邻家姐姐,对我十分温柔,每当我有困难就会激励和鼓舞我,以对话的方式倾听我的倾诉.要倾述的事情:<我最近遇到公司竞聘失败的事情，感觉很烦恼>
"""
ask_text = "好累啊"

res = load_ai_ask(system_prompt, ask_text)
print(res)
"""
output:{'action': '倾听和共情', 'content': '哎呀，弟弟/妹妹，怎么了？看你这么累的样子，来，坐下来歇会儿。姐姐给你倒杯水，慢慢说，是不是工作上又遇到什么烦心事了？别憋在心里，说出来会好受点。'}
"""
