import asyncio
class CalculatorTool:
    name = "calculator"
    description = "计算两个数字的加、减、乘、除。"

    async def execute(self, operation, a, b):
        if (
                isinstance(a, bool)
                or isinstance(b, bool)
                or not isinstance(a, (int, float))
                or not isinstance(b, (int, float))
        ):
            raise ValueError("a和b必须是数字")

        if operation == "add":
            return a + b

        if operation == "subtract":
            return a - b

        if operation == "multiply":
            return a * b

        if operation == "divide":
            if b == 0:
                raise ValueError("除数不能为0")
            return a / b

        raise ValueError(f"不支持的运算：{operation}")

    def to_openai_tool(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "add",
                                "subtract",
                                "multiply",
                                "divide"
                            ],
                            "description": "要执行的运算"
                        },
                        "a": {
                            "type": "number",
                            "description": "第一个数字"
                        },
                        "b": {
                            "type": "number",
                            "description": "第二个数字"
                        }
                    },
                    "required": ["operation", "a", "b"],
                    "additionalProperties": False
                }
            }
        }

if __name__ == "__main__":
    tool = CalculatorTool()
    print(tool.to_openai_tool())