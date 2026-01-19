import uuid
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver

from .config import (
    MODEL_NAME,
    POS_AGENT_PROMPT,
    NEG_AGENT_PROMPT,
    FINAL_AGENT_PROMPT,
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

def create_pos_agent():
    return create_agent(
        model= ChatOllama(model="mistral"),
        tools=[get_positive_news, get_technical_signals],
        system_prompt=POS_AGENT_PROMPT,
        name="positive_agent",
    )

def create_neg_agent():
    return create_agent(
        model=ChatOllama(model="mistral"),
        tools=[get_negative_news, get_technical_signals],
        system_prompt=NEG_AGENT_PROMPT,
        name="negative_agent",
    )

def create_final_agent():
    return create_agent(
        model=MODEL_NAME,
        tools=[get_market_sentiment, make_decision],
        system_prompt=FINAL_AGENT_PROMPT,
        name="final_agent",
    )


def create_supervisor_agent():
    pos_agent = create_pos_agent()
    neg_agent = create_neg_agent()
    final_agent = create_final_agent()

    supervisor = create_supervisor(
        supervisor_name="InvestmentSupervisor",
        model=ChatOpenAI(model=MODEL_NAME),
        agents=[pos_agent, neg_agent, final_agent],
        prompt=SUPERVISOR_PROMPT,
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile(checkpointer=MemorySaver())
    
    return supervisor