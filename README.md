📈 Investment Debate Agent System
Tento projekt je multi-agentový systém postavený na frameworku LangGraph, ktorý simuluje finančnú debatu o akciách. Systém využíva troch špecializovaných agentov riadených supervízorom, aby používateľovi poskytol vyvážený pohľad na investíciu (Bullish vs. Bearish) doplnený o technickú analýzu.

🚀 Funkcie
Multi-Agent Debate: Pozitívny a negatívny agent proti sebe argumentujú v dvoch kolách.

Technická Analýza: Automatické sťahovanie historických dát z yfinance a výpočet kĺzavých priemerov (MA50, MA200).

Web Search: Integrácia s Tavily Search pre získavanie najnovších správ z trhu.

Decision Engine: Finálny agent vyhodnocuje silu argumentov a robí rozhodnutie (BUY/SELL/HOLD).

Interaktívne CLI: Jednoduché prostredie v termináli pre zadávanie akciových symbolov.

🏗️ Architektúra Agentov
Positive Agent: Hľadá rastové faktory, zisky a býčie technické signály.

Negative Agent: Hľadá riziká, hrozby a medvedie technické signály.

Final Agent: Nestranný arbiter, ktorý sleduje sentiment trhu a robí finálny verdikt.

Supervisor: Riadi tok konverzácie a zabezpečuje správne poradie argumentácie a záverečné zhrnutie.

🛠️ Inštalácia
Klonovanie repozitára:

Bash
git clone https://github.com/tvoje-meno/investment-debate-agents.git
cd investment-debate-agents
Inštalácia závislostí:

Bash
pip install -r requirements.txt
(Poznámka: Uisti sa, že máš nainštalované knižnice: langchain, langgraph, langgraph-supervisor, langchain-openai, langchain-tavily, yfinance, pandas, python-dotenv.)

Konfigurácia API kľúčov:
Vytvor súbor src/keys.env a pridaj tvoje kľúče:

Útržok kódu
OPENAI_API_KEY=tvoj_openai_kluc
TAVILY_API_KEY=tvoj_tavily_kluc
🖥️ Použitie
Spusti hlavný skript:

Bash
python main.py
Postup v aplikácii:

Zadaj symbol akcie (napr. AAPL, TSLA, NVDA).

Ak systém nemá lokálne dáta, stiahne ich z Yahoo Finance.

Sleduj debatu agentov v reálnom čase.

Prečítaj si finálne rozhodnutie a zhrnutie od supervízora.

📁 Štruktúra projektu
main.py - Vstupný bod aplikácie, riadi cyklus sťahovania dát a spúšťanie analýzy.

agents.py - Definícia agentov a nastavenie langgraph-supervisor.

tools.py - Nástroje pre agentov (Tavily search, technická analýza, rozhodovacia logika).

config.py - Systémové prompty pre jednotlivé roly.

utils.py - Pomocné funkcie pre formátovaný výstup do terminálu.
