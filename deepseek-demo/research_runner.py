import asyncio
import json

from planner import generate_plan
from orchestrator import run_tasks
from summarizer import generate_report


def run_research(query, memory_context=""):
    print("正在生成计划......", flush=True)
    plan = generate_plan(query, memory_context)
    data = json.loads(plan)
    results = asyncio.run(run_tasks(data["sub_tasks"]))

    with open("task_answers.md", "w", encoding="utf-8") as f:
        for item in results:
            f.write(f"# {item['task_id']}\n\n")
            f.write(f"## 问题\n\n{item['question']}\n\n")
            f.write(f"## 回答\n\n{item['answer']}\n\n")

    print("正在汇总报告……", flush=True)
    final_report = generate_report(query, results)

    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(f"# 原始问题\n\n{query}\n\n")
        f.write(final_report)

    print("已保存子任务答案：task_answers.md")
    print("已保存最终报告：final_report.md")
    return final_report, results
