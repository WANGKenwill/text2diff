import gradio as gr

from src.core.diff import text2diff, diff2html, apply_diff



def process(origin_text, text_input):
    diff = text2diff(origin_text, text_input)
    result = diff2html(origin_text, diff)
    return f"<pre>{result}</pre>", origin_text, diff

def apply(origin_text, diff):
    return f"<pre>{apply_diff(origin_text, diff)}</pre>"


# 示例数据
examples = [
        ["""AI正在深刻改变我们的世界。从医疗诊断到自动驾驶，AI技术正在各个领域发挥重要作用。
在医疗领域，AI可以帮助医生更准确地诊断疾病。在交通领域，自动驾驶技术有望减少交通事故。
然而，AI的发展也带来了一些挑战。我们需要确保AI的使用是负责任的，符合伦理规范。
专家们认为，AI应该服务于人类，而不是取代人类。未来，AI将与人类协同工作，创造更美好的世界。""",
         """1. 把"我们的"改成"大家的"
2. 在"医疗诊断"前添加"先进的"
3. 在"交通事故"后添加"，提高道路安全"
4. 删除"一些"
"""],
    [
        """AI is profoundly changing our world. 
From medical diagnosis to autonomous driving, AI technology is playing an important role in various fields.
In the medical field, AI can help doctors diagnose diseases more accurately. 
In the transportation field, autonomous driving technology has the potential to reduce traffic accidents.
However, the development of AI also brings some challenges. 
We need to ensure that the use of AI is responsible and complies with ethical standards.
Experts believe that AI should serve humanity, not replace it. 
In the future, AI will work collaboratively with humans to create a better world.""",
        """1. Change "our" to "the"
2. Add "advanced" before "medical diagnosis"
3. Add ", improving road safety" after "traffic accidents"
4. Delete "some"
"""
    ]
    ]

with gr.Blocks() as demo:
    origin_state = gr.State()
    diff_state = gr.State()

    with gr.Column():
        gr.Markdown("# text2diff:自然语言描述修改文本")
        gr.Markdown("## 第一步：输入待修改的文本")
        with gr.Tabs() as tabs:
            with gr.TabItem("原文", id="origin_tab"):
                origin_input = gr.Textbox(lines=30, show_label=False)
            with gr.TabItem("修订", id="h5_preview_tab"):
                h5_preview = gr.HTML()
                apply_btn = gr.Button("确认修改", variant="primary")


        gr.Markdown("## 第二步：描述你想要怎么修改, 再点击“AI修订”")
        revision_input = gr.TextArea()
        with gr.Row():
            create_diff = gr.Button("AI修订", variant="primary")

        gr.Markdown("## 示例：点击示例内容，再点击“AI修订”看效果")
        # 添加示例组件
        examples = gr.Examples(
            examples=examples,
            inputs=[origin_input, revision_input],
            label="示例",
        )

        

    
    # 绑定事件
    create_diff.click(
        lambda: [gr.update(selected="h5_preview_tab"), gr.update(interactive=False)],
        inputs=None,
        outputs=[tabs, apply_btn],
        queue=False  # 立即执行UI更新
    ).then(
        fn=process,
        inputs=[origin_input, revision_input],
        outputs=[h5_preview, origin_state, diff_state]
    ).then(
        lambda: gr.update(interactive=True),
        inputs=None,
        outputs=apply_btn
    )

    apply_btn.click(
        fn=apply,
        inputs=[origin_state, diff_state],
        outputs=[h5_preview]
    ).then(
        lambda: gr.update(interactive=False),
        inputs=None,
        outputs=apply_btn
    )




    

 

# 启动界面
demo.launch()