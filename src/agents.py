import uuid
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver

from .config import (
    MODEL_NAME,
    FINAL_AGENT_PROMPT,
    OVERALL_AGENT_PROMPT,
    SUPERVISOR_PROMPT,
)

from .tools import(
    get_positive_news,
    get_negative_news,
    get_market_sentiment,
    make_decision,
    get_technical_signals,
)

load_dotenv("src/keys.env")

def create_overall_agent():
    return create_agent(
        model= ChatOpenAI(model=MODEL_NAME),
        tools=[get_positive_news, get_technical_signals,get_negative_news],
        system_prompt=OVERALL_AGENT_PROMPT,
        name="overall_agent",
    )

def create_final_agent():
    return create_agent(
        model=ChatOpenAI(model=MODEL_NAME),
        tools=[get_market_sentiment, make_decision],
        system_prompt=FINAL_AGENT_PROMPT,
        name="final_agent",
    )


def create_supervisor_agent():
    overall_agent = create_overall_agent()
    final_agent = create_final_agent()

    supervisor = create_supervisor(
        supervisor_name="InvestmentSupervisor",
        model=ChatOpenAI(model=MODEL_NAME),
        agents=[overall_agent, final_agent],
        prompt=SUPERVISOR_PROMPT,
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile(checkpointer=MemorySaver())
    
    return supervisor