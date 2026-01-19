from langchain_core.messages import convert_to_messages, ToolMessage, AIMessage

def pretty_print_message(message, indent=False):
    """Vypíše len čistý text správy bez technických metadát."""
    text = str(message.content)

    if not text.strip():
        return

    if indent:
        text = "\n".join("\t" + line for line in text.split("\n"))
    
    print(text)

def pretty_print_messages(update, last_message=False):
    """Filtruje a vypisuje správy z debaty tak, aby boli prehľadné."""
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0: return
        is_subgraph = True
        
    for node_name, node_update in update.items():
        messages_raw = node_update.get("messages", [])
        if not messages_raw:
            continue
            
        messages = convert_to_messages(messages_raw)
        
        for m in messages:
            # 1. Ignorujeme technické ToolMessages (stavové správy nástrojov)
            if isinstance(m, ToolMessage):
                continue
            
            # 2. Ignorujeme routovacie AI správy (napr. "Transferring back to...")
            content_str = str(m.content).strip()
            if not content_str:
                continue
            
            routing_phrases = ["Transferring back to", "transferring to", "Successfully transferred"]
            if any(phrase in content_str for phrase in routing_phrases):
                if hasattr(m, 'tool_calls') and m.tool_calls:
                    continue
                if len(content_str) < 60: # Krátke technické oznámenia preskočíme
                    continue

            # 3. Vypíšeme len podstatný obsah
            print(f"\n[ NODE: {node_name.upper()} ]")
            pretty_print_message(m, indent=is_subgraph)
            print("=" * 50)