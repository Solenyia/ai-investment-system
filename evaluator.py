import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

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
                change_val = row[20] 
                
                if isinstance(change_val, str):
                    change_val = float(change_val.replace(',', '.'))
                
                if pd.isna(change_val) or decision == "NAN":
                    continue

                status = ""
                matrix_cat = ""
                is_success = False
                THRESHOLD = 0.05 

                # Alpha výnos
                bot_return = change_val if decision == "BUY" else 0
                alpha = bot_return - change_val

                # Logika vyhodnotenia
                if decision == "BUY" and change_val > THRESHOLD:
                    status = "🌟 CRITICAL SUCCESS"
                    matrix_cat = "True Positive"
                    is_success = True
                elif decision == "SELL" and change_val < -THRESHOLD:
                    status = "🌟 CRITICAL SUCCESS"
                    matrix_cat = "True Negative (Defense)"
                    is_success = True
                elif decision == "BUY" and change_val < -THRESHOLD:
                    status = "❌ CRITICAL FAILURE"
                    matrix_cat = "False Positive (Bull Trap)"
                    is_success = False
                elif (decision == "SELL" or decision == "HOLD") and change_val > THRESHOLD:
                    status = "❌ CRITICAL FAILURE"
                    matrix_cat = "False Negative"
                    is_success = False
                elif change_val <= 0 and (decision == "HOLD" or decision == "SELL"):
                    status = "✅ SUCCESS (Defense)"
                    matrix_cat = "True Negative (Defense)"
                    is_success = True
                elif change_val > 0 and decision == "BUY":
                    status = "✅ SUCCESS (Profit)"
                    matrix_cat = "True Positive"
                    is_success = True
                else:
                    status = "❌ FAILURE"
                    matrix_cat = "False Positive" if decision == "BUY" else "False Negative"
                    is_success = False

                results.append({
                    'Architektúra': current_arch,
                    'Ticker': ticker,
                    'Rozhodnutie': decision,
                    'Zmena_Trh': change_val,
                    'Alpha': alpha,
                    'Verdikt': status,
                    'Matrix_Kategoria': matrix_cat,
                    'Bodovanie': 1 if is_success else 0
                })
            except:
                continue

    return pd.DataFrame(results)

def generate_charts(df):
    if df.empty: return
    sns.set_theme(style="whitegrid")
    
    # Graf 1: Úspešnosť architektúr
    plt.figure(figsize=(10, 6))
    arch_acc = df.groupby('Architektúra')['Bodovanie'].mean() * 100
    ax = arch_acc.plot(kind='bar', color='skyblue')
    plt.title('Celková úspešnosť podľa architektúr (%)', fontsize=14)
    plt.ylabel('Úspešnosť v %')
    plt.ylim(0, 100)
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}%', (p.get_x() + 0.15, p.get_height() + 2))
    plt.tight_layout()
    plt.savefig('graf_uspesnost.png')
    
    # Graf 2: Alpha výnos (Pridaná hodnota)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Ticker', y='Alpha', hue='Architektúra')
    plt.axhline(0, color='black', linewidth=1)
    plt.title('Alpha výnos (Pridaná hodnota bota oproti trhu)', fontsize=14)
    plt.ylabel('Alpha (0.1 = +10%)')
    plt.tight_layout()
    plt.savefig('graf_alpha.png')
    print("\n📈 Grafy boli uložené: 'graf_uspesnost.png' a 'graf_alpha.png'")

if __name__ == "__main__":
    df_results = evaluate_professional_analysis('Statistics Bachelor.xlsx')
    if not df_results.empty:
        # Výpis štatistík do konzoly
        print(df_results[['Architektúra', 'Ticker', 'Rozhodnutie', 'Verdikt']].to_string(index=False))
        print(f"\nPriemerná Alpha: {df_results['Alpha'].mean():+.2%}")
        
        # Generovanie grafov
        generate_charts(df_results)
        df_results.to_csv('finalny_report.csv', index=False, encoding='utf-8-sig')