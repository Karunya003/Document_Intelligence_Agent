# agent/agent.py
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agent.tools import core_tools, dynamic_tools
from agent.prompts import STRUCTURED_PROMPT

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, request_timeout=120)

# Conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def build_agent():
    """
    Build a JSON-structured agent for document Q&A
    with conversation memory and dynamic tools.
    """

    all_tools = core_tools + dynamic_tools

    tools_str = "\n".join([f"- {tool.name}: {tool.description}" for tool in all_tools])
    tool_names_str = ", ".join([tool.name for tool in all_tools])
    
    
    agent = create_structured_chat_agent(
        llm=llm,
        tools=all_tools,
        prompt=STRUCTURED_PROMPT.partial(tools=tools_str, tool_names=tool_names_str),
    )

    executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=memory,
        verbose=True,
        max_iterations=50,
        handle_parsing_errors=True,
    )

    return executor
