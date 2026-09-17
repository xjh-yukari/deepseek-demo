from research_runner import run_research
from memory_store import save_memory
from memory_retriever import retrieve_memory_context
from session_manager import start_new_session
def main():
    print("请输入研究问题；输入 开启新对话 清空记忆；输入 exit 退出。")

    while True:
        query = input("\n你的问题:").strip()

        if query.lower() == "exit":
            print("已退出。")
            break

        if not query:
            continue

        if query == "开启新对话":
            start_new_session()
            print("已开启新对话，历史记忆已清空。")
            continue

        memory_context = retrieve_memory_context(query)
        print(f"读取历史资料：{len(memory_context)} 字符", flush=True)
        report, results = run_research(query, memory_context)
        save_memory(query, results)
        print(f"\n{report}")

if __name__ == "__main__":
    main()
