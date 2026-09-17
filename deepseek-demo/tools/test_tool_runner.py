import asyncio
from tools.tool_runner import run_with_tools


async def main():
    answer = await run_with_tools(
        "请先用计算器计算12345乘6789，再用计算器将结果除以5。"
    )
    print("最终回答：", answer)


if __name__ == "__main__":
    asyncio.run(main())
