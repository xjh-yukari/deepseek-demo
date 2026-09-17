import json

from model_client import request_with_tools
from tools.registry import ToolRegistry


async def run_with_tools(query, max_rounds=5):
    registry = ToolRegistry()
    definitions = registry.get_definitions()

    messages = [
        {
            "role": "system",
            "content": (
                "请回答用户的问题。涉及算术时使用计算器。"
                "根据工具结果继续处理，完成后给出最终答案。"
            )
        },
        {"role": "user", "content": query}
    ]

    for _ in range(max_rounds):
        message = request_with_tools(messages, definitions)

        if not message.tool_calls:
            return message.content

        messages.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            arguments = json.loads(tool_call.function.arguments)

            result = await registry.execute(
                tool_name=tool_call.function.name,
                arguments=arguments
            )

            print(f"[工具] {tool_call.function.name} 执行完成")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    raise RuntimeError("已达到工具调用轮数上限，尚未获得最终回答")