from openai import OpenAI, AsyncOpenAI, DefaultHttpxClient, DefaultAsyncHttpxClient
from env_config import api_key, base_url, model
import argparse#终端
import time

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=DefaultHttpxClient(trust_env=False)
)

def call_model(messages, label="模型请求"):
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    elapsed = time.perf_counter() - start
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None)
    reasoning_tokens = getattr(details, "reasoning_tokens", None)
    print(
        f"[{label}] 耗时：{elapsed:.1f}秒 | "
        f"模型：{response.model} | "
        f"输入：{usage.prompt_tokens if usage else '未知'} token | "
        f"总输出：{usage.completion_tokens if usage else '未知'} token | "
        f"其中思考："
        f"{reasoning_tokens if reasoning_tokens is not None else '未提供'} token",
        flush=True
    )

    return response.choices[0].message.content

async def call_model_async(
    messages,
    label="异步模型请求",
    thinking=None
):
    start = time.perf_counter()

    async with AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=DefaultAsyncHttpxClient(trust_env=False)
    ) as async_client:
        request_options = {}

        if thinking is not None:
            request_options["extra_body"] = {
                "thinking": {
                    "type": "enabled" if thinking else "disabled"
                }
            }

        response = await async_client.chat.completions.create(
            model=model,
            messages=messages,
            **request_options
        )

    elapsed = time.perf_counter() - start
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None)
    reasoning_tokens = getattr(details, "reasoning_tokens", None)
    print(
        f"[{label}] 耗时：{elapsed:.1f}秒 | "
        f"模型：{response.model} | "
        f"输入：{usage.prompt_tokens if usage else '未知'} token | "
        f"总输出：{usage.completion_tokens if usage else '未知'} token | "
        f"其中思考："
        f"{reasoning_tokens if reasoning_tokens is not None else '未提供'} token",
        flush=True
    )

    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()
    messages = [
        {"role": "user", "content": args.query}
    ]
    print("准备发送的问题：", messages[0]["content"])

    print("正在请求 DeepSeek……", flush=True)
    answer = call_model(messages)
    print("已收到响应", flush=True)

    print("DeepSeek的回答:", answer)

    with open("report.md", "w", encoding="utf-8") as f:
        f.write(f"# 问题\n\n{args.query}\n\n")
        f.write(f"## 回答\n\n{answer}\n")

def request_with_tools(messages, tools):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        extra_body={
            "thinking": {"type": "disabled"}
        }
    )

    return response.choices[0].message

if __name__ == "__main__":
    main()
