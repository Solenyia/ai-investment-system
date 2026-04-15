import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import random

def evaluate_professional_analysis(excel_path):
    if not os.path.exists(excel_path):
        print(f"Chyba: Súbor '{excel_path}' nebol nájdený.")
        return pd.DataFrame()

    try:
        df = pd.read_excel(excel_path, header=None, engine='openpyxl')
    except Exception as e:
        print(f"Chyba pri otváraní Excelu: {e}")
        return pd.DataFrame()
    
    results = []
    current_arch = "Neznáma sekcia"
    valid_tickers = ['AAPL', 'MSFT', 'GOOG', 'META', 'TSLA', 'NVDA', 'NVD']

    for index, row in df.iterrows():
        cell_val = str(row[2]).lower() if pd.notnull(row[2]) else ""
        if 'architektura' in cell_val:
            current_arch = str(row[2]).strip()
            continue
            
        ticker = str(row[2]).strip()
        if ticker in valid_tickers:
            try:
                decision = str(row[3]).strip().upper() if pd.notnull(row[3]) else "NAN"
                
                # Náhodný baseline (čistá náhoda)
                random_decision = random.choice(['BUY', 'HOLD', 'SELL'])
                
                change_val = row[20] 
                if isinstance(change_val, str):
                    change_val = float(change_val.replace(',', '.'))
                
                if pd.isna(change_val) or decision == "NAN":
                    continue

                THRESHOLD = 0.05 

                def get_detailed_stats(dec, change):
                    status = ""
                    matrix_cat = ""
                    is_success = False
                    
                    if dec == "BUY" and change > THRESHOLD:
                        status, matrix_cat, is_success = "🌟 CRITICAL SUCCESS", "True Positive", True
                    elif dec == "SELL" and change < -THRESHOLD:
                        status, matrix_cat, is_success = "🌟 CRITICAL SUCCESS", "True Negative (Defense)", True
                    elif dec == "BUY" and change < -THRESHOLD:
                        status, matrix_cat, is_success = "❌ CRITICAL FAILURE", "False Positive (Bull Trap)", False
                    elif (dec == "SELL" or dec == "HOLD") and change > THRESHOLD:
                        status, matrix_cat, is_success = "❌ CRITICAL FAILURE", "False Negative", False
                    elif change <= 0 and (dec == "HOLD" or dec == "SELL"):
                        status, matrix_cat, is_success = "✅ SUCCESS (Defense)", "True Negative (Defense)", True
                    elif change > 0 and dec == "BUY":
                        status, matrix_cat, is_success = "✅ SUCCESS (Profit)", "True Positive", True
                    else:
                        status, matrix_cat, is_success = "❌ FAILURE", ("False Positive" if dec == "BUY" else "False Negative"), False
                    
                    return status, matrix_cat, (1 if is_success else 0)

                # Vyhodnotenie bota
                status, matrix_cat, score = get_detailed_stats(decision, change_val)
                
                # Vyhodnotenie náhody
                _, _, random_score = get_detailed_stats(random_decision, change_val)

                # Alpha výnos: rozdiel medzi botovým výnosom a trhovou zmenou
                bot_return = change_val if decision == "BUY" else 0
                alpha = bot_return - change_val

                results.append({
                    'Architektúra': current_arch,
                    'Ticker': ticker,
                    'Rozhodnutie': decision,
                    'Random_Rozhodnutie': random_decision,
                    'Zmena_Trh': change_val,
                    'Alpha': alpha,
                    'Verdikt': status,
                    'Matrix_Kategoria': matrix_cat,
                    'Bodovanie': score,
                    'Random_Bodovanie': random_score
                })
            except:
                continue

    return pd.DataFrame(results)

def generate_charts(df):
    if df.empty: return
    sns.set_theme(style="whitegrid")
    
    plt.figure(figsize=(10, 6))
    acc = df.groupby('Architektúra')[['Bodovanie', 'Random_Bodovanie']].mean() * 100
    ax = acc.plot(kind='bar', color=['skyblue', 'salmon'], figsize=(10, 6))
    plt.title('Celková úspešnosť: Bot vs Náhoda (%)', fontsize=14)
    plt.ylabel('Úspešnosť v %')
    plt.ylim(0, 100)
    plt.legend(['Môj Bot', 'Náhodný Baseline'])
    plt.tight_layout()
    plt.savefig('graf_uspesnost.png')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Ticker', y='Alpha', hue='Architektúra')
    plt.axhline(0, color='black', linewidth=1)
    plt.title('Alpha výnos (Pridaná hodnota bota oproti trhu)', fontsize=14)
    plt.tight_layout()
    plt.savefig('graf_alpha.png')
    print("\n📈 Grafy boli uložené: 'graf_uspesnost.png' a 'graf_alpha.png'")

if __name__ == "__main__":
    df_results = evaluate_professional_analysis('Statistics Bachelor.xlsx')
    if not df_results.empty:
        print(df_results[['Architektúra', 'Ticker', 'Rozhodnutie', 'Verdikt']].to_string(index=False))
        print(f"\nPriemerná Alpha: {df_results['Alpha'].mean():+.2%}")
        
        print("\n--- POROVNANIE ÚSPEŠNOSTI S NÁHODOU ---")
        print(df_results.groupby('Architektúra')[['Bodovanie', 'Random_Bodovanie']].mean())
        
        generate_charts(df_results)
        df_results.to_csv('finalny_report.csv', index=False, encoding='utf-8-sig')