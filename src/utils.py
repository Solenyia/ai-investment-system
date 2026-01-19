from langchain_core.messages import convert_to_messages, ToolMessage, AIMessage

def pretty_print_message(message, indent=False):
    """Vypíše len čistý text správy bez technických metadát."""
    text = str(message.content)

    if not text.strip():
        return

    if indent:
        text = "\n".join("\t" + line for line in text.split("\n"))
    
    print(text)

from langchain_core.messages import convert_to_messages, ToolMessage, AIMessage

def pretty_print_messages(update, last_message=False):
    """Filters and prints messages to show the debate flow without repetition."""
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
            # 1. Skip technical ToolMessages and empty content
            if isinstance(m, ToolMessage) or not str(m.content).strip():
                continue
            
            # 2. Skip technical routing messages
            content_str = str(m.content).strip()
            routing_phrases = ["Transferring back to", "transferring to", "Successfully transferred"]
            if any(phrase in content_str for phrase in routing_phrases):
                continue

            # 3. CRITICAL FIX: Identify the actual sender
            # Sub-agents in a supervisor setup put their name in the 'name' field.
            # If 'name' is missing, we use the node_name.
            sender_name = getattr(m, "name", node_name)
            if sender_name is None:
                sender_name = node_name
            
            sender_display = sender_name.upper()

            # 4. Skip showing the user's initial question under the supervisor's name
            if sender_display == "INVESTMENTSUPERVISOR" and m.type == "human":
                continue

            print(f"\n[ NODE: {sender_display} ]")
            pretty_print_message(m, indent=is_subgraph)
            print("=" * 50)