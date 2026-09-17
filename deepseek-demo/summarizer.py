from model_client import call_model


def generate_report(query, results):
    research_text = ""

    for item in results:
        research_text += (
            f"任务编号：{item['task_id']}\n"
            f"子问题：{item['question']}\n"
            f"材料：{item['context_answer']}\n\n"
        )

    messages = [
        {
            "role": "system",
            "content": (
                "你是研究报告整理助手。请根据子任务结果回答原始问题。"
                "合并重复内容，指出冲突和信息不足之处。"
                "没有可靠来源的信息应明确说明，不要编造来源。"
                "以分析任务的结论为线索，用其他任务材料补充依据并检查一致性。"
                "不要扩展新话题或重复铺陈背景。先回答问题，再给关键依据和限制。"
                "默认尽量控制在800字以内，用户明确要求详细报告时按需展开。"
                "使用Markdown格式输出。"
            )
        },
        {
            "role": "user",
            "content": (
                f"原始问题：{query}\n\n"
                f"子任务结果：\n{research_text}"
            )
        }
    ]

    return call_model(messages, label="最终汇总")
