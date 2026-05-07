import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI


async def main():
    client = MultiServerMCPClient(
        {
            "context7": {
                "url": "https://mcp.context7.com/mcp",
                "transport": "streamable_http",
            },
            "met-museum": {
                "command": "npx",
                "args": ["-y", "metmuseum-mcp"],
                "transport": "stdio",
            },
        }
    )

    model = ChatOpenAI(model="gpt-5-nano")
    tools = await client.get_tools()
    config = {"configurable": {"thread_id": "conversation_id"}}

    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful agent with access to code library documentation and the Met Museum collection.",
                },
                {
                    "role": "user",
                    "content": "Give a brief introduction of what you do and the tools you can access.",
                },
            ]
        },
        config=config,
    )
    print(response["messages"][-1].content)

    while True:
        choice = input("\n1. Ask a question\n2. Quit\n> ").strip()
        if choice == "1":
            query = input("Question: ").strip()
            response = await agent.ainvoke({"messages": query}, config=config)
            print(response["messages"][-1].content)
        else:
            print("Goodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
