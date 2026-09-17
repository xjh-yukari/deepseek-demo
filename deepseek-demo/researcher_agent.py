from model_client import call_model, call_model_async
async def run_task(task, dependency_results):
    context = ""

    for task_id, answer in dependency_results.items():
        context += f"任务 {task_id} 的结果：\n{answer}\n\n"

    if dependency_results:
        task_instructions = (
            "你负责根据前置材料进行分析。输出结论、支撑理由、冲突和信息缺口。"
            "不要复述整份前置材料，不写最终报告的开场和结尾。"
            "尽量控制在600字以内，保留影响结论的条件、关键数字和已有来源。"
        )
    else:
        task_instructions = (
            "你负责整理当前子问题需要的精简材料。直接列出3至6个关键要点。"
            "尽量控制在500字以内，不写完整报告，不扩展无关历史、配置或百科细节。"
            "保留影响判断的关键事实、适用条件和已有来源。"
        )

    messages = [
        {
            "role": "system",
            "content": (
                task_instructions
                + "资料不足或存在冲突时明确说明，不要编造来源。"
                "当前没有联网工具，不得声称已经搜索或核验实时资料。"
            )
        },
        {
            "role": "user",
            "content": (
                f"当前任务：{task['description']}\n\n"
                f"前置任务结果：\n{context}"
            )
        }
    ]
    return await call_model_async(
        messages,
        label=f"执行 {task['task_id']}"
    )

def run_search_task(task):
    question = task["description"]

    messages = [
        {
            "role":"user",
            "content":question
        }
    ]

    return call_model(messages)

def run_analysis_task(task):
    question = task["description"]

    messages = [
        {
            "role": "system",
            "content": "你负责比较，归纳和分析已有信a息。"
        },
        {
            "role": "user",
            "content": question
        }
    ]

    return call_model(messages)
