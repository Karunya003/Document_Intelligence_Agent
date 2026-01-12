from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agent.tools import core_tools, dynamic_tools
from agent.prompts import CONVERSATION_PROMPT, EXTRACTION_PROMPT 
import json
import re

# Initialize LLMs
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, request_timeout=300)

# Separate memories
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True
)

# Direct extraction function
def extract_document_insights(document_text: str) -> dict:
    """Direct LLM call for initial document extraction (no tools)"""
    chain = EXTRACTION_PROMPT | llm
    
    try:
        # Get response
        response = chain.invoke({
            "document_text": document_text[:6000]
        })
        
        # Clean and parse JSON
        content = response.content.strip()
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        
        # Parse JSON
        data = json.loads(content)
        
        return data
        
    except Exception as e:
        # Fallback
        return {
            "summary": "Extracted from document",
            "entities": [],
            "risks": [],
            "metrics": {}
        }

# Build conversation agent
def build_conversation_agent():
    all_tools = core_tools + dynamic_tools
    
    tools_str = "\n".join([f"- {tool.name}: {tool.description}" for tool in all_tools])
    tool_names_str = ", ".join([tool.name for tool in all_tools])
    
    # Create conversation agent with CONVERSATION_PROMPT
    agent = create_react_agent(
        llm=llm,
        tools=all_tools,
        prompt=CONVERSATION_PROMPT.partial(
            tools=tools_str, 
            tool_names=tool_names_str
        ),
    )
    
    executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=conversation_memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        early_stopping_method="force",
        max_execution_time=30,
        return_intermediate_steps=False,
    )
    
    return executor

# Initialize conversation agent
conversation_agent = build_conversation_agent()