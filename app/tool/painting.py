# https://platform.openai.com/docs/guides/images
# 2024/6/11
# zhangzhong

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from openai import OpenAI

client = OpenAI(
    api_key="sk-ZwL10bd1199a7d452d6c1f614426f8a9b7678138996PT0kP",  # type: ignore
    base_url="https://api.gptsapi.net/v1",
)


@tool
def dalle_tool(prompt: str) -> str:
    """
    DALL-E tool
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
    )

    print(response)
    return response.data[0].url
