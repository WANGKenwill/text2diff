import gradio as gr

from src.core.diff import text2diff, diff2html, apply_diff



def process(origin_text, text_input):
    diff = text2diff(origin_text, text_input)
    result = diff2html(origin_text, diff)
    return f"<pre>{result}</pre>", origin_text, diff

def apply(origin_text, diff):
    return f"<pre>{apply_diff(origin_text, diff)}</pre>"

with gr.Blocks() as demo:
    origin_state = gr.State()
    diff_state = gr.State()

    with gr.Column():
        gr.Markdown("# text2diff:自然语言描述修改文本")
        gr.Markdown("## 第一步：输入待修改的文本")
        with gr.Tabs() as tabs:
            with gr.TabItem("原文", id="origin_tab"):
                txt_input = gr.Textbox(lines=30, show_label=False)
            with gr.TabItem("修订", id="h5_preview_tab"):
                h5_preview = gr.HTML()
                apply_btn = gr.Button("确认修改", variant="primary")


        gr.Markdown("## 第二步：描述你想要怎么修改")
        text_input = gr.TextArea()
        with gr.Row():
            create_diff = gr.Button("AI修订", variant="primary")

       

    # 绑定事件
    create_diff.click(
        fn=process,
        inputs=[txt_input, text_input],
        outputs=[h5_preview, origin_state, diff_state]
    ).then(
        lambda: gr.update(selected="h5_preview_tab"),
        inputs=None,
        outputs=tabs
    ).then(
        lambda: gr.update(interactive=True),
        inputs=None,
        outputs=apply_btn
    )
    
    # 绑定事件
    create_diff.click(
        lambda: [gr.update(selected="h5_preview_tab"), gr.update(interactive=False)],
        inputs=None,
        outputs=[tabs, apply_btn],
        queue=False  # 立即执行UI更新
    ).then(
        fn=process,
        inputs=[txt_input, text_input],
        outputs=[h5_preview, origin_state, diff_state]
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