import pytest
from src.core.diff import split_text_by_sentences, text2diff, apply_diff

# 测试用例数据
TEST_CASES_SPLIT = [
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
        [(0, 'He said "Hello." '), (17, 'She replied "Hi!"')]
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
    ),
    # 8. 有不能成句的残留部分
    (
        "第一句!！第二句??第三句。",
        [(0, '第一句!！'), (5, '第二句??'), (10, '第三句。')]
    )
]

@pytest.mark.parametrize("input_text, expected", TEST_CASES_SPLIT)
def test_split_text_by_sentences(input_text, expected):
    # 执行分割
    result = split_text_by_sentences(input_text)
    
    # 验证分割结果
    assert result == expected, f"分割结果不匹配：\n输入: {input_text}\n预期: {expected}\n实际: {result}"
    
    # 验证重新拼接是否等于原文
    reconstructed_text = ''.join([chunk for _, chunk in result])
    assert reconstructed_text == input_text, f"重新拼接不匹配：\n原文: {input_text}\n拼接: {reconstructed_text}"

TEST_CASES_DIFF = [
    (
        # 输入原文
        """AI正在深刻改变我们的世界。从医疗诊断到自动驾驶，AI技术正在各个领域发挥重要作用。
在医疗领域，AI可以帮助医生更准确地诊断疾病。在交通领域，自动驾驶技术有望减少交通事故。
然而，AI的发展也带来了一些挑战。我们需要确保AI的使用是负责任的，符合伦理规范。
专家们认为，AI应该服务于人类，而不是取代人类。未来，AI将与人类协同工作，创造更美好的世界。""",
        # 输入修订指令
        """
        1. 把"我们的"改成"大家的"
        2. 在"医疗诊断"前添加"先进的"
        3. 在"交通事故"后添加"，提高道路安全"
        4. 删除"一些"
        """,
        # 预期 replacements
        [(8, 11, '大家的'), (15, 19, '先进的医疗诊断'), (82, 86, '交通事故，提高道路安全'), (100, 102, '')],
        # 预期修订后的文本
        """AI正在深刻改变大家的世界。从先进的医疗诊断到自动驾驶，AI技术正在各个领域发挥重要作用。
在医疗领域，AI可以帮助医生更准确地诊断疾病。在交通领域，自动驾驶技术有望减少交通事故，提高道路安全。
然而，AI的发展也带来了挑战。我们需要确保AI的使用是负责任的，符合伦理规范。
专家们认为，AI应该服务于人类，而不是取代人类。未来，AI将与人类协同工作，创造更美好的世界。"""
    ),

    # 可以继续添加更多测试用例
]

@pytest.mark.parametrize("text, instructions, expected_replacements, expected_revision", TEST_CASES_DIFF)
def test_text2diff_and_apply_diff(text, instructions, expected_replacements, expected_revision):
    # 测试 text2diff
    replacements = text2diff(text, instructions)
    assert replacements == expected_replacements

    # 测试 apply_diff
    revision = apply_diff(text, replacements)
    assert revision == expected_revision

# 添加单独运行的功能
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__])