# https://python.langchain.com/v0.2/docs/integrations/tools/tavily_search/
# 2024/6/11
# zhangzhong


import os

from langchain_community.tools.tavily_search import TavilySearchResults

os.environ["TAVILY_API_KEY"] = "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"
search_tool = TavilySearchResults()
