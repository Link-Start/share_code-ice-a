# 导入所需的标准库和第三方库
import json
import requests
import os

# ===================== 配置项 =====================
# API密钥（请在此处填写你的实际密钥）
API_KEY = ""  

# API请求的基础URL
API_BASE_URL = "https://api.longcat.chat/openai/v1/chat/completions"


# ===================== 核心函数 =====================
def parse_ai_response(response: dict) -> list | None:
    """
    解析AI返回的响应数据，提取其中的JSON格式信息
    
    Args:
        response (dict): AI接口返回的原始响应字典
        
    Returns:
        list | None: 解析成功返回信息列表，失败返回None
    """
    try:
        # 1. 提取AI回复的文本内容（核心路径：choices -> 第一个元素 -> message -> content）
        content = response['choices'][0]['message']['content']
        
        # 2. 定位并提取包裹在```json和```之间的JSON字符串
        # 找到起始标记位置并跳过标记本身
        start_idx = content.find('```json') + len('```json')
        # 找到结束标记位置
        end_idx = content.rfind('```')
        # 提取并清理JSON字符串（去除首尾空白字符）
        json_str = content[start_idx:end_idx].strip()
        
        # 3. 将JSON字符串转换为Python列表（信息）
        train_data = json.loads(json_str)
        
        return train_data
    
    # 捕获可能的异常：KeyError(键不存在)、IndexError(索引越界)、JSONDecodeError(JSON解析失败)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ 解析AI响应数据时出错: {e}")
        return None

def clean_html(raw_html):
    """
    清洗 HTML，移除无关标签以节省 Token
    """
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    # 移除 script, style, svg 等无关标签
    for script in soup(["script", "style", "svg", "head", "iframe"]):
        script.decompose()
        
    # 获取纯文本或保留部分结构的 HTML (视模型能力而定，通常保留 tag 有助于定位)
    # 这里我们保留精简后的 HTML 结构
    return str(soup.body)[:10000] # 截取前 10000 字符防止超长

def ask_ai_train_parse(role_prompt: str, text_html: str, save_path: str) -> None:
    """
    调用AI接口解析网页中的信息，并将结果保存为JSON文件
    
    Args:
        role_prompt (str): 系统角色提示词，定义AI的行为
        text_html (str): 包含信息的网页HTML文本
        save_path (str): 解析结果的保存路径
    """
    # 1. 构建请求头（包含认证信息和内容类型）
    headers = {
        "Authorization": f"Bearer {API_KEY}",  # API认证方式
        "Content-Type": "application/json"     # 请求体为JSON格式
    }

    # 2. 构建请求体数据
    request_data = {
        "model": "LongCat-Flash-Chat",         # 使用的AI模型名称
        "messages": [                          # 对话消息列表
            {"role": "system", "content": role_prompt},  # 系统角色提示
            {"role": "user", "content": text_html}       # 用户输入（网页HTML文本）
        ],
        "max_tokens": 1000,                    # 生成的最大令牌数（控制响应长度）
        "temperature": 0                     # 生成随机性（0-1，值越高越随机）
    }

    try:
        # 3. 发送POST请求调用AI接口
        print(f"🔄 正在调用AI接口解析信息...")
        response = requests.post(
            url=API_BASE_URL,
            headers=headers,
            json=request_data,
            timeout=30  # 设置30秒超时，避免无限等待
        )
        # 检查HTTP响应状态码，非200则抛出异常
        response.raise_for_status()
        
        # 4. 解析AI响应数据
        train_data = parse_ai_response(response.json())
        
        # 5. 保存解析结果到指定文件
        if train_data is not None:
            with open(save_path, 'w', encoding='utf-8') as f:
                # 格式化保存JSON数据（确保中文正常显示，缩进4个空格）
                json.dump(train_data, f, ensure_ascii=False, indent=4)
            print(f"✅ 信息解析完成，已保存至: {save_path}")
        else:
            print(f"❌ 信息解析失败，未生成文件")

        # 可选：打印原始响应（方便调试）
        # print("📝 AI接口原始响应：", json.dumps(response.json(), ensure_ascii=False, indent=2))
        
    # 捕获网络请求相关异常
    except requests.exceptions.RequestException as e:
        print(f"❌ 调用AI接口时发生网络错误: {e}")
    # 捕获文件操作相关异常
    except IOError as e:
        print(f"❌ 保存解析结果时发生文件错误: {e}")
        
# ===================== 主程序执行 =====================
if __name__ == "__main__":
    # 定义AI的系统角色提示词（明确要求提取信息并返回JSON）
    schema_desc = """
    请提取网页中的文章列表。返回格式必须是合法的 JSON，结构如下：
    {
        "articles": [
            {"title": "文章标题", "publish_date": "发布日期", "author": "作者", "summary": "简短摘要"}
        ]
    }
    """
    role_prompt = f"""
    你是一个专业的数据解析助手。请根据以下 HTML 内容，提取相关数据。
    
    {schema_desc}
    
    注意：
    1. 只返回纯 JSON 字符串，不要使用 markdown 格式。
    2. 如果找不到数据，返回空列表。
    
    HTML 内容片段：
    {clean_content}
    """
    # 待解析的网页HTML文本（替换为实际的HTML内容）
    html_text = ""
    
    # 调用函数执行解析并保存结果
    ask_ai_train_parse(role_prompt, html_text, "test_parse.json")
