from typing import List, Tuple
import ell
from src.core import MODEL_NAME

import re
import json


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
      "original": <需要修改的原文，不能为空字符串，因为需要利用原文定位>,
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
2. 从目标文本往前追溯start标记符，不要往后找
3. 位置标记符不是文本内容的一部分，不要将其包含在original中
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
        
        # 获取原始文本
        original = origin_text[start:end]
        
        # 判断修改类型
        if not content:  # 删除
            html_lines.append(
                f"<span style='color:red;text-decoration:line-through'>{original}</span>"
            )
        elif start == end:  # 新增
            html_lines.append(
                f"<span style='color:green;font-weight:bold'>{content}</span>"
            )
        elif original in content:  # 修改（包含原文）
            # 找到原文在 new_content 中的位置
            original_start = content.find(original)
            original_end = original_start + len(original)
            
            # 添加新增部分（绿色）
            if original_start > 0:
                html_lines.append(
                    f"<span style='color:green;font-weight:bold'>{content[:original_start]}</span>"
                )
            
            # 添加原文部分（原格式）
            html_lines.append(original)
            
            # 添加新增部分（绿色）
            if original_end < len(content):
                html_lines.append(
                    f"<span style='color:green;font-weight:bold'>{content[original_end:]}</span>"
                )
        else:  # 完全修改
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
    separator_pattern = re.compile(r"""
    # 核心内容：匹配非终止符部分（直到遇到终止符）
    [^。！？!?]+?                # 排除终止符，但允许句点（用于处理版本号等）
    # 终止符部分（支持连续多个终止符）
    (?:
        \. (?= \s | $ | ['"]\s )   # 句点需后接空格/结尾/引号+空格（避免误伤版本号）
      | [。！？!?]+               # 允许连续多个终止符（如 "??"、"!！"）
    )
    # 可选的后置引号及其后续空白（支持引号后直接结束或跟空格）
    (?: ['"] (?:\s|$))?
    # 捕获剩余的空白（确保分割位置准确）
    \s*                           
""", re.VERBOSE)

    matches = re.finditer(separator_pattern, text)
    result = []
 

    start = 0
    for match in matches:
        end = match.end()
        chunk = text[start:end]
        if chunk:
            result.append((start, chunk))
            start = end

    # 处理无匹配的情况
    if not result:
        return [(0, text)]

    # 处理末尾残留字符
    if start < len(text):
        result.append((start, text[start:]))

    
    return result

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
