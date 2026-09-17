import asyncio
from researcher_agent import run_task
from compressor import compress_text

async def run_tasks(tasks):
    pending = list(tasks)
    results_by_id = {}
    results = []

    async def execute(task):
        dependencies = {
            dep: results_by_id[dep]
            for dep in task.get("dependencies", [])
        }

        print(f"开始：{task['task_id']}", flush=True)
        answer = await run_task(task, dependencies)

        if len(answer) > 2000:
            print(f"正在压缩：{task['task_id']}", flush=True)
            context_answer = await compress_text(
                answer,
                task_id=task["task_id"]
            )
            print(
                f"[{task['task_id']}] 压缩完成："
                f"{len(answer)} → {len(context_answer)} 字符",
                flush=True
            )
        else:
            context_answer = answer

        print(f"完成：{task['task_id']}", flush=True)

        return {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "question": task["description"],
            "dependencies": task.get("dependencies", []),
            "answer": answer,
            "context_answer": context_answer
        }

    while pending:
        ready = [
            task for task in pending
            if all(
                dep in results_by_id
                for dep in task.get("dependencies", [])
            )
        ]

        if not ready:
            raise ValueError("无法继续：存在循环依赖或不存在的依赖编号")

        batch_results = await asyncio.gather(
            *(execute(task) for task in ready)
        )

        for result in batch_results:
            results_by_id[result["task_id"]] = result["context_answer"]
            results.append(result)

        pending = [task for task in pending if task not in ready]

    return results
