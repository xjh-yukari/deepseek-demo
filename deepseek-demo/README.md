# DeepSeek Research Agent Demo

一个用于学习 LLM 应用开发的 Python 项目：将问题拆解为三个子任务，按依赖并发执行，按需压缩答案，最终生成 Markdown 报告。支持独立单次研究、带本地记忆的连续提问，以及独立的计算器工具调用演示。

参考学习项目：[qiqihezh/deepresearch-agent](https://github.com/qiqihezh/deepresearch-agent)。本项目为简化学习实现，不是原项目的完整复刻，也不代表原项目作者维护。

> 当前研究流程没有联网搜索。`search` 是任务标签，实际仍由模型根据已有知识作答。请勿把输出当作经过实时检索核验的事实。`tools/web_search.py` 目前只是空文件。

## 已实现

- 提示词生成 JSON 计划，任务 1、2 独立并发，任务 3 使用前两者的结果进行分析。
- 单个答案超过 2000 字符才调用摘要压缩，原文与摘要分别保留。
- 汇总器使用三个任务的精简材料，生成最终报告。
- 单次入口不读写记忆；连续入口检索历史、执行研究并追加记忆。
- 本地 384 维 Embedding、NumPy 相似度排序、SQLite 向量缓存。
- 工具注册表及多轮计算器调用演示，尚未接入研究主流程。
- 分阶段耗时、输入输出 Token 日志。

## 环境要求

- 推荐从 **Python 3.11、64 位**开始，与本项目已有运行环境一致。其他 Python 版本没有在本项目中验证；不要因为系统装了 3.14 就直接用它创建环境，机器学习依赖的兼容性需要单独检查。
- 安装 Git 和 uv。uv 管理环境与依赖，不需要同时安装 Anaconda。
- DeepSeek API Key、可调用的模型名称和账户可用额度。网页聊天账户不等同于 API 配置；运行真实请求可能收费。
- 下载 Python、依赖和首次下载 Embedding 模型时需要网络。CPU 可运行，不要求 NVIDIA 显卡；当前开发环境使用 CPU 版 PyTorch。
- 本项目没有完整依赖锁文件。`requirements.txt` 是直接依赖清单，不保证未来安装结果与开发环境完全一致。

## 快速开始（Windows PowerShell）

先克隆你看到的这个仓库，并进入仓库根目录。如果通过 ZIP 下载，先解压再进入包含 `run_single.py` 的文件夹。不要克隆参考项目来运行本 README 的命令。

```powershell
uv python install 3.11
uv venv --python 3.11 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
Copy-Item .env.example .env
```

用编辑器打开 `.env`，填入自己的配置：

```dotenv
DEEPSEEK_API_KEY=替换为你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=替换为账户当前可用的模型ID
```

模型名称必须以服务商当前支持的 ID 为准，不要照抄过期教程。代码的压缩与工具演示使用 DeepSeek 的 `thinking` 扩展参数，换其他兼容服务时也要检查参数支持情况。

检查环境，不发送模型请求：

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe env_config.py
```

最后一条只打印是否读取到密钥、地址和模型名称，不打印密钥本身。PyCharm 中选择已有解释器 `.venv\Scripts\python.exe`，不要重复创建 `.venv1`。

以上命令直接使用虚拟环境的 Python，无须激活，也不会遇到激活脚本执行策略的问题。Linux/macOS 的 Python 路径为 `./.venv/bin/python`，复制命令使用 `cp .env.example .env`。

## 使用方式

所有命令从仓库根目录运行。

### 单次研究（不读写历史记忆）

```powershell
.\.venv\Scripts\python.exe run_single.py --query "Python列表和元组有什么区别？"
```

终端显示进度和统计，最终正文查看 `final_report.md`，各子任务原文查看 `task_answers.md`。两个文件每次运行都会覆盖。`--query` 是程序参数，不能单独作为 PowerShell 命令执行。

### 连续提问（使用历史记忆）

```powershell
.\.venv\Scripts\python.exe run_repl.py
```

- 输入问题：检索历史后执行研究，成功后追加保存记忆，并打印报告。
- 输入 `exit`：退出。
- 输入 `开启新对话`：**清空全部当前历史记忆及向量缓存，不保留旧会话档案**。
- 按 `Ctrl+C`：中断本地运行；已发送的请求可能仍产生费用。

记忆原文保存在项目目录 `memory.json`，向量缓存保存在 `memory_vectors.db`。即使退出程序，文件仍然存在。请勿同时开启多个进程写同一份记忆。

### 独立演示

```powershell
# 单次直接模型问答，保存 report.md；会调用 API
.\.venv\Scripts\python.exe model_client.py --query "用一句话介绍Python"
# 多轮计算器工具调用；会调用 API
.\.venv\Scripts\python.exe -m tools.test_tool_runner
# 摘要压缩演示；会调用 API
.\.venv\Scripts\python.exe test_compressor.py
# 本地向量演示；首次可能下载模型，不调用 DeepSeek
.\.venv\Scripts\python.exe memory_embedder.py
.\.venv\Scripts\python.exe memory_retriever.py
```

工具演示要用 `-m tools.test_tool_runner`，不要直接运行文件路径。命名为 `test_` 的现有脚本是演示，不是完整的自动化测试套件。

## 执行流程

```text
单次问题 ───────────────────┐
连续问题 → 检索历史记忆 ─────┤
                           ↓
                     Planner 生成计划
                           ↓
              task_1              task_2
              回答/按需压缩        回答/按需压缩
                   └──────┬──────┘
                          ↓
                  task_3 分析/按需压缩
                          ↓
             Summarizer 汇总三个 context_answer
                          ↓
                     保存最终报告
                          ↓
                  仅连续入口追加记忆
```

基本研究需要 5 次模型请求：规划 1 次、子任务 3 次、汇总 1 次；三个答案都触发压缩时共 8 次，不含 SDK 可能的重试。任务 1、2 的等待可以重叠，但任务 3 和最终汇总仍然有顺序依赖。

## 文件与技术

| 文件 | 职责 |
| --- | --- |
| `env_config.py` / `model_client.py` | 环境配置、统一模型调用、耗时与 Token 统计 |
| `planner.py` | 问题拆解和 JSON 计划 |
| `orchestrator.py` | 基于依赖分批并发调度 |
| `researcher_agent.py` | 单个子任务执行，当前无联网工具 |
| `compressor.py` / `summarizer.py` | 长答案摘要、最终报告 |
| `research_runner.py` | 共享研究流程与报告保存 |
| `run_single.py` / `run_repl.py` | 无记忆单次入口、带记忆连续入口 |
| `memory_store.py` / `session_manager.py` | JSON 记忆持久化、清空会话 |
| `memory_embedder.py` / `memory_retriever.py` | 文本向量、SQLite 缓存、相似度检索 |
| `tools/` | 计算器、注册表和独立工具调用循环 |

技术栈：Python、OpenAI Python SDK（连接 DeepSeek）、python-dotenv、asyncio、Sentence Transformers、NumPy、标准库 SQLite/JSON/argparse。复习与简历描述见 [技术总结](docs/TECH_STACK.md)，发布注意事项见 [发布检查](docs/PUBLISH_CHECKLIST.md)。

## 记忆检索说明

模型为 `sentence-transformers/all-MiniLM-L6-v2`，本地生成归一化的 384 维向量。对历史问题和当前问题编码，点积等价于这些归一化向量的余弦相似度。SQLite 按“模型名称 + 问题文本”缓存向量；NumPy 逐条计算并排序，**不是专用向量数据库或近似最近邻索引**。

当前最多选取 3 条记录，阈值为 0.55，并始终保留最近一条。因此不相关的上一问也可能进入上下文。只编码问题，不编码整个答案。模型主要面向英文，中文效果需要实际评估；相似度不是正确率或概率。

首次有历史可检索时可能下载模型，之后每个进程仍需加载权重。HF Hub 的匿名访问提示不是模型加载失败，访问受限时按服务提示配置令牌，令牌同样不要提交。

## 已知限制与排错

- 没有真实搜索、网页阅读、来源核验、红蓝对抗、自动重规划或系统评测；不要声称完全复刻原项目。
- 计划主要依靠提示词约束，没有完整的结构校验与错误恢复。非法 JSON、接口异常会中断当前流程。
- 没有应用层超时、重试、并发上限与预算控制。已有 SDK 默认行为不能替代完整容错。
- 压缩会增加请求，300 字是软目标；只有答案正文超过 2000 字符才触发，思考 Token 不参与这个字符判断。
- 记忆暂无数量和总 Token 上限。完整历史及回答以明文存储，选中的内容会发送给模型服务商，请勿输入不应上传的敏感信息。
- 当前 HTTP 客户端 `trust_env=False`，不自动读取系统/环境代理。它来自本地代理故障排查，不是通用网络加速设置；必须经代理联网的环境需要另行配置，不能关闭 TLS 验证来绕过错误。
- `ModuleNotFoundError`：确认安装依赖与运行使用同一个 `.venv`；工具测试从根目录按上述 `-m` 命令运行。
- API 401/额度错误：检查密钥与账户；模型或参数错误：核实模型 ID 和接口支持；连接错误：检查网络与代理；不要公开完整配置或密钥。
- 不保证答案事实准确、检索相关或压缩不丢信息。性能应对同一问题重复测量，不用单次结果宣称固定提速比例。

## 发布与来源

`.gitignore` 排除密钥、虚拟环境、IDE 配置、个人记忆、SQLite 缓存及生成报告。上传前仍须检查暂存区；忽略规则不会移除已经被 Git 跟踪的文件。

原项目 README 标注 MIT，但当前本地参考副本未发现对应 LICENSE 文件。发布前应核实上游实际授权，保留适用的版权声明，不要仅凭徽章替原作者确定许可证。本仓库尚未新增许可证；为自己原创部分选择许可证前，请先厘清复用代码的授权。
#   d e e p s e e k - d e m o  
 #   d e e p s e e k - d e m o  
 #   d e e p s e e k - d e m o  
 