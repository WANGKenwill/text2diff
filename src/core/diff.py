from typing import List, Tuple
import ell
from src.core import MODEL_NAME

import re
import json

def split_into_sentences(paragraph):
    # Regular expression pattern
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
    sentences = re.split(sentence_endings, paragraph)    
    return sentences

def split_text_by_sentences3(text: str) -> List[Tuple[int, str]]:
    """
    按句子或双换行符分割文本，并返回每块的文本及其在原始字符串中的起始位置。
    分隔符（如句号、感叹号、问号）会保留在每句的末尾。
    
    Args:
        text (str): 原始文本
    
    Returns:
        List[Tuple[int, str]]: 每块的起始位置和文本
    """
    # 优化后的正则表达式
    separator_pattern = r'(?:[^。！？]*[。！？]|[^.!?]*[.!?](?=\s|$))(?:\s*["\']?)?|\n\s*\n'
    matches = re.finditer(separator_pattern, text)
    result = []
    
    for match in matches:
        start_pos = match.start()
        chunk = match.group().strip()
        if chunk:  # 确保不添加空字符串
            result.append((start_pos, chunk))
    
    return result

def split_text_by_sentences2(text: str) -> List[Tuple[int, str]]:
    """
    按句子或双换行符分割文本，并返回每块的文本及其在原始字符串中的起始位置。
    分隔符（如句号）会保留在每句的末尾。

    Args:
        text (str): 原始文本

    Returns:
        List[Tuple[int, str]]: 每块的起始位置和文本
    """
    # 正则表达式：匹配句子结束符号或双换行符，保留分隔符
    separator_pattern = r"(.+?[.!?]|\n\n)(?:\s+|$)"
    matches = re.findall(separator_pattern, text, flags=re.DOTALL)
    
    # 计算每块的起始位置
    result = []
    current_pos = 0
    for chunk in matches:
        result.append((current_pos, chunk))
        current_pos += len(chunk)
    
    return result


def rebuild_text_with_positions(chunks_with_starts: List[Tuple[str, int]]) -> str:
    """
    将分割后的文本块重新拼接，并在每块前插入起始位置标记。

    Args:
        chunks_with_starts (List[Tuple[str, int]]): 每块的文本及其起始位置

    Returns:
        str: 重新拼接后的文本，包含起始位置标记
    """
    result = []
    for start, chunk in chunks_with_starts:
        # 插入起始位置标记
        result.append(f"‖start:{start}‖{chunk}")
    return "".join(result)






@ell.simple(model=MODEL_NAME)
def text2diff_llm(text_with_pos:str, revision_text:str):
    """
你的任务是基于原文和修改建议生成修改数据结构。

关于位置标记：
- 原文中的‖start:数字‖是位置标记符，标记了后续文本的起始位置
- 在定位original内容时，使用该内容往前追溯的最近一个‖start:数字‖中的数字作为start值
- 严格使用标记符中的数字，不要自行计算或估算位置

输出格式：
[
    {

      "sentence_start": <使用original内容往前追溯的最近一个位置标记符里的数字>,
      "original": <需要修改的原文>,
      "content": <修改后的内容>


    }
]


示例原文：
‖start:0‖这是一个测试句子‖start:6‖这是第二个测试句子。

示例修改建议：
把"第二个"改为"第三个"

示例输出：
[
    {
        "sentence_start": 6,
        "original": "第二个",
        "content": "第三个"
    }
]

注意：
1. 严格使用标记符中的数字作为start值，不要计算
2. 位置标记符不是文本内容的一部分，不要将其包含在original中
"""
    return f"现在请处理以下内容：\n原文：\n{text_with_pos}\n修改建议：\n{revision_text}"

def apply_diff(origin_text: str, replacements: list) -> str:
    """
    应用修改到原始文本。
    """

    # 1. 按照 start 位置降序排序，从后往前替换
    sorted_replacements = sorted(replacements, key=lambda x: x[0], reverse=True)
    
    # 2. 依次应用每个修改
    result = origin_text
    for start, end, content in sorted_replacements:
        result = result[:start] + content + result[end:]
    
    return result


def diff2md(origin_text: str, replacements: List[Tuple[int, int, str]]) -> str:
    """
    将修改信息渲染为Markdown格式
    
    Args:
        origin_text (str): 原始文本
        revisions (List[Tuple[int, int, str]]): 修改列表，每个元素是 (start, end, content)
        
    Returns:
        str: Markdown格式的修改信息
    """
    # 1. 按照start位置升序排序
    sorted_replacements = sorted(replacements, key=lambda x: x[0])
    
    # 2. 构建Markdown内容
    md_lines = []
    current_pos = 0
    
    for start, end, content in sorted_replacements:
        # 添加未修改部分
        if current_pos < start:
            md_lines.append(origin_text[current_pos:start])
        
        # 添加修改部分
        original = origin_text[start:end]
        md_lines.append(f"~~{original}~~ → **{content}**")
        
        current_pos = end
    
    # 添加最后未修改部分
    if current_pos < len(origin_text):
        md_lines.append(origin_text[current_pos:])
    
    return "".join(md_lines)

def diff2html(origin_text: str, replacements: List[Tuple[int, int, str]]) -> str:
    """
    将修改信息渲染为HTML格式
    
    Args:
        origin_text (str): 原始文本
        replacements (List[Tuple[int, int, str]]): 修改列表，每个元素是 (start, end, content)
        
    Returns:
        str: HTML格式的修改信息
    """
    # 1. 按照start位置升序排序
    sorted_replacements = sorted(replacements, key=lambda x: x[0])
    
    # 2. 构建HTML内容
    html_lines = []
    current_pos = 0
    
    for start, end, content in sorted_replacements:
        # 添加未修改部分
        if current_pos < start:
            html_lines.append(origin_text[current_pos:start])
        
        # 添加修改部分
        original = origin_text[start:end]
        html_lines.append(
            f"<span style='color:red;text-decoration:line-through'>{original}</span>"
            f" → "
            f"<span style='color:green;font-weight:bold'>{content}</span>"
        )
        
        current_pos = end
    
    # 添加最后未修改部分
    if current_pos < len(origin_text):
        html_lines.append(origin_text[current_pos:])
    
    return "".join(html_lines)

def exact_revision(origin_text: str, revisions: dict) -> List[Tuple[int, int, str]]:
    """
    获取精确的替换位置，返回一个列表，元素是 (start, end, content) 组成的元组。

    Args:
        origin_text (str): 原始文本
        revisions (dict): 修改内容，包含 "revisions" 字段

    Returns:
        List[Tuple[int, int, str]]: 替换位置列表，每个元素是 (start, end, content)
    """
    result = []
    for rev in revisions:
        start = rev["sentence_start"]
        original = rev["original"]
        content = rev["content"]
        
        # 从 start 位置开始搜索 original
        match_pos = origin_text.find(original, start)
        if match_pos != -1:
            # 如果找到匹配的 original，记录替换位置
            end = match_pos + len(original)
            result.append((match_pos, end, content))
    
    return result



def build_text_with_pos(text):
    result = split_text_by_sentences(text)
    return rebuild_text_with_positions(result)

def text2diff(origin_text:str, revision_text:str):
    result = build_text_with_pos(origin_text)
    resp = text2diff_llm(result, revision_text)
    return exact_revision(origin_text, json.loads(resp))


def split_text_by_sentences(text: str) -> List[Tuple[int, str]]:
    """
    按句子分割文本，返回每个句子及其起始位置。
    保留句末标点，特殊处理邮箱和网址中的点号。
    
    Args:
        text (str): 原始文本
    Returns:
        List[Tuple[int, str]]: 每句的起始位置和内容
    """
    # 正则表达式：匹配完整句子，点号后必须是空白或结束
    # separator_pattern = r'[^。！？!?]+?(?:\.(?=\s|$)|[。！？!?])[\s]*'
    # 暂时用到这里。，现在就用例5没过，.和"同时在的时候会有问题
    # separator_pattern = r'[^。！？!?]+?(?:\.(?=\s|$|[\'"]\s)|[。！？!?])[\s]*'
    separator_pattern = r'[^。！？!?]+?(?:\.(?=\s|$|[\'"]\s*)|[。！？!?])[\s]*'

    matches = re.finditer(separator_pattern, text)
    result = []
    
    for match in matches:
        chunk = match.group()
        if chunk:  # 确保不添加空字符串
            result.append((match.start(), chunk))
    
    return result

# 测试用例
def test_sentence_splitter():
    test_cases = [
        # 1. 基本英文句子
        (
            "Hello world. This is a test! How are you?",
            [(0, "Hello world. "), (13, "This is a test! "), (29, "How are you?")]
        ),
        
        # 2. 包含邮箱
        (
            "My email is test.name@example.com. Next sentence!",
            [(0, "My email is test.name@example.com. "), (35, "Next sentence!")]
        ),
        
        # 3. 包含网址
        (
            "Visit www.example.com. Then contact us!",
            [(0, "Visit www.example.com. "), (23, "Then contact us!")]
        ),
        
        # 4. 包含省略号
        (
            "Think about it... Then decide!",
            [(0, "Think about it... "), (18, "Then decide!")]
        ),
        
        # 5. 带引号的对话
        (
            'He said "Hello." She replied "Hi!"',
            [(0, 'He said "Hello." '), (16, 'She replied "Hi!"')]
        ),
        
        # 6. 版本号
        (
            "Using version 2.0.1. Next line.",
            [(0, "Using version 2.0.1. "), (21, "Next line.")]
        ),
        
        # 7. 混合中英文
        (
            "Hello世界。This是test.com网站。Good!",
            [(0, "Hello世界。"), (8, "This是test.com网站。"), (24, "Good!")]
        )
    ]

    passed_count = 0
    failed_count = 0

    print("\n开始执行测试用例...\n")
    for i, (input_text, expected) in enumerate(test_cases, 1):
        try:
            result = split_text_by_sentences(input_text)
            
            # 新增：验证重新拼接是否等于原文
            reconstructed_text = ''.join([chunk for _, chunk in result])
            reconstruction_match = reconstructed_text == input_text
            
            if result == expected and reconstruction_match:
                print(f"✅ 测试用例 {i} 通过")
                passed_count += 1
            else:
                print(f"❌ 测试用例 {i} 失败")
                print(f"   输入: {input_text}")
                print(f"   预期: {expected}")
                print(f"   实际: {result}")
                
                if not reconstruction_match:
                    print(f"   重新拼接不匹配！")
                    print(f"   原文长度: {len(input_text)}")
                    print(f"   拼接长度: {len(reconstructed_text)}")
                    print(f"   原文: {input_text}")
                    print(f"   拼接: {reconstructed_text}")
                print()
                
                failed_count += 1
        except Exception as e:
            print(f"⚠️ 测试用例 {i} 出现异常")
            print(f"   错误信息: {str(e)}")
            failed_count += 1
    
    print(f"\n测试结果：通过 {passed_count} 个，失败 {failed_count} 个")
    if failed_count == 0:
        print("🎉 所有测试用例通过！")
    else:
        print("💔 存在失败的测试用例")


if __name__ == "__main__":

    # 原文示例
    text = """AI正在深刻改变我们的世界。从医疗诊断到自动驾驶，AI技术正在各个领域发挥重要作用。
在医疗领域，AI可以帮助医生更准确地诊断疾病。在交通领域，自动驾驶技术有望减少交通事故。
然而，AI的发展也带来了一些挑战。我们需要确保AI的使用是负责任的，符合伦理规范。
专家们认为，AI应该服务于人类，而不是取代人类。未来，AI将与人类协同工作，创造更美好的世界。"""


    replacements = text2diff(text, """
    1. 把"我们的"改成"大家的"
    2. 在"医疗诊断"前添加"先进的"
    3. 在"交通事故"后添加"，提高道路安全"
    4. 删除"一些"
    """)

    print(f"\n{replacements}")

    revision = apply_diff(text, replacements)
    print(f"\n{revision}")

    # test_sentence_splitter()
