from langchain_openai import ChatOpenAI, OpenAIEmbeddings

chat_model = ChatOpenAI(
    api_key="sk-ZwL10bd1199a7d452d6c1f614426f8a9b7678138996PT0kP",  # type: ignore
    base_url="https://api.gptsapi.net/v1",
    streaming=False,
)

embedding = OpenAIEmbeddings(
    api_key="sk-ZwL10bd1199a7d452d6c1f614426f8a9b7678138996PT0kP",  # type: ignore
    base_url="https://api.gptsapi.net/v1",
)
