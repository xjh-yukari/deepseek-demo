from model_client import call_model_async


async def compress_text(text, task_id=""):
    messages = [
        {
            "role": "system",
            "content": (
                "请压缩以下任务结果，尽量控制在300字以内。"
                "保留关键事实、数字、适用条件和不确定性。"
                "如果原文有来源编号或链接，请保留。"
                "删除重复和无关内容，不要添加原文没有的信息。"
                "只输出压缩后的内容。"
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]

    return await call_model_async(
        messages,
        label=f"压缩 {task_id}",
        thinking=False
    )

