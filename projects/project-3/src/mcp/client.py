import asyncio
from fastmcp import Client

class ComplianceMCPClient:
    def __init__(self):
        self.client = Client("http://127.0.0.1:8001/mcp")

    async def _call_tool_async(self, tool_name: str, arguments: dict):
        async with self.client:
            result = await self.client.call_tool(tool_name, arguments)
            return result

    async def _read_resource_async(self, uri: str):
        async with self.client:
            result = await self.client.read_resource(uri)
            return result

    async def _get_prompt_async(self, prompt_name: str, arguments: dict):
        async with self.client:
            result = await self.client.get_prompt(prompt_name, arguments)
            return result

    def call_tool(self, tool_name: str, arguments: dict):
        return asyncio.run(self._call_tool_async(tool_name, arguments))

    def read_resource(self, uri: str):
        return asyncio.run(self._read_resource_async(uri))

    def get_prompt(self, prompt_name: str, arguments: dict):
        return asyncio.run(self._get_prompt_async(prompt_name, arguments))