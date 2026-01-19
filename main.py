import os
import sys
import uuid
from src.agents import create_supervisor_agent
from src.utils import pretty_print_messages
import yfinance as yf
import pandas as pd


def importer(stock_symbol):
    ticker = stock_symbol
    data = yf.download(ticker, period="5y")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.to_csv(f"{ticker}_historical_data.csv")

    data.to_csv(f"{ticker}_historical_data.csv")
    print(f"Downloaded {ticker} data and saved to {ticker}_historical_data.csv")

def hello():
    print("Hello! This is the Investment Debate Agent System.")
    print("Pos and Neg agents will debate on a stock of your choice." \
    " Then the Final agent will make a decision based on their arguments." )

def analyze_stock(supervisor, stock_symbol):
    print(f"\nStarting analysis for stock: {stock_symbol.upper()}\n")

    user_query = f"Analyze {stock_symbol} stock. I need a debate between a bull and a bear to decide."

    unique_run_id = str(uuid.uuid4()).split('-')[0] 
    thread_id = f"analysis-{stock_symbol.lower()}-{unique_run_id}"

    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query,
                }
            ]
        },
        config={"configurable": {"thread_id": thread_id}}
    ):
        pretty_print_messages(chunk, last_message=False)

def main():
    
    hello()

    print("\nCreating agents...")
    supervisor = create_supervisor_agent()
    print("Agents created successfully.")

    while True:
        try:
            stock_symbol = input("\nEnter a stock symbol to analyze (or type 'exit' to quit): ").strip()
            
            if stock_symbol.lower() == 'exit':
                print("Exiting the program. Goodbye!")
                break
            
            if not stock_symbol:
                print("Please enter a valid stock symbol.")
                continue
            
            if f"{stock_symbol.upper()}_historical_data.csv" not in os.listdir():
                print(f"Historical data for {stock_symbol} not found locally. Downloading...")
                importer(stock_symbol)

            analyze_stock(supervisor, stock_symbol)
            
        except KeyboardInterrupt:
            print("\nExiting the program. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()