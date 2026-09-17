import asyncio

from compressor import compress_text


async def main():
    text = (
        "Python列表是可变序列，可以添加、删除和修改元素。"
        "元组是不可变序列，创建后不能替换其中的元素引用。"
        "但元组中包含的列表等可变对象，其内部内容仍然可以修改。"
    )

    summary = await compress_text(text, task_id="单独测试")
    print("摘要：", summary)


if __name__ == "__main__":
    asyncio.run(main())