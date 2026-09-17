import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
model = os.getenv("DEEPSEEK_MODEL")

if __name__ == "__main__":
    print("密钥已读取",bool(api_key))
    print("接口地址:",base_url)
    print("模型名称:",model)