from .calculator import CalculatorTool


class ToolRegistry:
    def __init__(self):
        calculator = CalculatorTool()

        self.tools = {
            calculator.name: calculator
        }

    def get_definitions(self):
        definitions = []

        for tool in self.tools.values():
            definitions.append(tool.to_openai_tool())

        return definitions

    async def execute(self, tool_name, arguments):
        tool = self.tools.get(tool_name)

        if tool is None:
            raise ValueError(f"找不到工具：{tool_name}")

        return await tool.execute(**arguments)