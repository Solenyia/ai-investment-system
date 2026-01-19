import os
import uuid
from docx import Document
from datetime import datetime

# Import tvojich funkcií z main.py
from main import importer, create_supervisor_agent

def extract_decision_from_final(text):
    """
    GPT-4o ako final_agent zvyčajne vráti text s rozhodnutím.
    Tento parser hľadá kľúčové slová.
    """
    if not text or "Successfully transferred" in text:
        return None
    
    text_upper = text.upper()
    if "BUY" in text_upper: return "BUY"
    if "SELL" in text_upper or "AVOID" in text_upper: return "SELL"
    if "HOLD" in text_upper: return "HOLD"
    return None

def run_benchmark(stock_symbol="AAPL", iterations=5):
    doc = Document()
    doc.add_heading(f'Hybrid Benchmark Report: Mistral (Agents) + GPT-4o (Logic)', 0)
    
    if f"{stock_symbol.upper()}_historical_data.csv" not in os.listdir():
        importer(stock_symbol)
    
    # Tu sa vytvorí supervisor (GPT-4o), ktorý riadi Mistral agentov
    supervisor = create_supervisor_agent()

    for i in range(1, iterations + 1):
        print(f"\n>>> BEŽÍ TEST {i}/{iterations}...")
        
        thread_id = f"hybrid-bench-{uuid.uuid4().hex[:4]}"
        user_query = f"Should I invest in {stock_symbol} stock?"
        
        final_decision_found = "NEURČITÉ"
        full_final_reasoning = ""
        supervisor_summary = ""

        # Sledujeme stream správ
        for chunk in supervisor.stream(
            {"messages": [{"role": "user", "content": user_query}]},
            config={"configurable": {"thread_id": thread_id}}
        ):
            for node_name, node_update in chunk.items():
                if "messages" in node_update:
                    msg_content = node_update["messages"][-1].content
                    
                    # 1. Zachytíme analýzu od final_agent (GPT-4o)
                    if node_name == "final_agent":
                        # Ignorujeme technické prechody, ukladáme len skutočný text
                        if "Successfully transferred" not in msg_content:
                            full_final_reasoning = msg_content
                            decision = extract_decision_from_final(msg_content)
                            if decision:
                                final_decision_found = decision

                    # 2. Zachytíme zhrnutie od supervisora (GPT-4o)
                    if node_name == "InvestmentSupervisor":
                        if "Successfully transferred" not in msg_content:
                            supervisor_summary = msg_content

        # Zápis do Wordu
        doc.add_heading(f'Test č. {i}', level=1)
        
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        cells = table.rows[0].cells
        cells[0].text = "VÝSLEDNÉ ROZHODNUTIE:"
        cells[1].text = final_decision_found
        
        doc.add_heading('Zhrnutie od Supervisora (GPT-4o):', level=2)
        doc.add_paragraph(supervisor_summary if supervisor_summary else "Zhrnutie chýba.")
        
        doc.add_heading('Argumentácia Final Agenta (GPT-4o):', level=2)
        doc.add_paragraph(full_final_reasoning if full_final_reasoning else "Detailné zdôvodnenie chýba.")
        
        doc.add_page_break()

    filename = f"Hybrid_Report_{stock_symbol}.docx"
    doc.save(filename)
    print(f"\n--- HOTOVO! Report uložený: {filename} ---")

if __name__ == "__main__":
    run_benchmark("AAPL", iterations=5)