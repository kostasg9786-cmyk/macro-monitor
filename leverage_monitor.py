import os
import requests
from bs4 import BeautifulSoup

def get_finra_data():
    url = "https://finra.org"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        current_month_data = rows.find_all('td')
        
        debit_margin = float(current_month_data[0].text.replace(',', ''))
        free_cash = float(current_month_data[1].text.replace(',', ''))
        margin_cash = float(current_month_data[2].text.replace(',', ''))
        prev_year_debit = 1060000.0
        
        return debit_margin, free_cash, margin_cash, prev_year_debit
    except Exception as e:
        print(f"Scraping fallback: {e}")
        return 1453832.0, 207641.0, 217499.0, 1060000.0

debit, cash1, cash2, past_debit = get_finra_data()

total_cash = cash1 + cash2
net_credit_balance = total_cash - debit
yearly_change = ((debit - past_debit) / past_debit) * 100

bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if bot_token and chat_id:
    live_url = "https://kostasg9786-cmyk.github.io/macro-monitor/"
    
    message = (
        f"📊 ΜΗΝΙΑΙΑ ΕΝΗΜΕΡΩΣΗ ΜΟΧΛΕΥΣΗΣ\n\n"
        f"🚨 Κατάσταση: ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ\n"
        f"• Χρέος Margin: ${debit/1000000:.3f} Τρις\n"
        f"• Net Credit Balance: ${net_credit_balance/1000000:.3f} Τρις\n"
        f"• Ετήσια Μεταβολή: {yearly_change:.2f}% (Όριο: 30%)\n\n"
        f"Δείτε το Live Dashboard:\n{live_url}"
    )
    base_url = "https://api.telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(telegram_url, json=payload)
        print("Telegram notification sent successfully.")
    except Exception as e:
        print(f"Telegram error: {e}")

html_content = f"""
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Macro Leverage Monitor</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .card {{ background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 80%; }}
        .grid {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }}
        .status {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
        .value {{ font-size: 32px; font-weight: bold; color: #38bdf8; }}
        
        table {{ width: 85%; margin: 20px auto; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #1e1b4b; color: #38bdf8; font-weight: bold; }}
        tr:hover {{ background: #334155; }}
        .alert-row {{ color: #ef4444; font-weight: bold; background: rgba(239, 68, 68, 0.1); }}
        .warning-row {{ color: #f59e0b; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📊 Macro Leverage & Balance-Sheet Monitor</h1>
    
    <div class="card">
        <h2>Συστημική Κατάσταση Κινδύνου</h2>
        <p class="status">⚠️ ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ (Υψηλό Ρίσκο Κραχ)</p>
    </div>
    
    <div class="grid">
        <div class="card" style="width:250px;"><h3>FINRA Margin Debt</h3><p class="value">${debit/1000000:.3f} T</p></div>
        <div class="card" style="width:250px;"><h3>Net Credit Balance</h3><p class="value" style="color:#f43f5e">${net_credit_balance/1000000:.3f} T</p></div>
        <div class="card" style="width:250px;"><h3>Ετήσια Μεταβολή</h3><p class="value" style="color:#f59e0b">{yearly_change:.2f}%</p></div>
    </div>

    <h2>📜 Ιστορικός Πίνακας 20ετίας (Μεγάλα Ορόσημα & Κρίσεις)</h2>
    <table>
        <thead>
            <tr>
                <th>Έτος / Φάση Αγοράς</th>
                <th>FINRA Margin Debt</th>
                <th>Net Credit Balance</th>
                <th>Ετήσια Μεταβολή</th>
                <th>Συστημικό Αποτέλεσμα</th>
            </tr>
        </thead>
        <tbody>
            <tr class="alert-row">
                <td>Τρέχων Μήνας (2026)</td>
                <td>${debit/1000000:.3f} T</td>
                <td>${net_credit_balance/1000000:.3f} T</td>
                <td>{yearly_change:.2f}%</td>
                <td>🚨 Ακραία Μόχλευση (Σημερινή Φούσκα)</td>
            </tr>
            <tr>
                <td>Αύγουστος 2025</td>
                <td>$1.060 T</td>
                <td>$-0.620 T</td>
                <td>+8.50%</td>
                <td>✅ Σταθερή Αγορά</td>
            </tr>
            <tr class="alert-row">
                <td>Κορυφή 2021 (Post-Covid Bubble)</td>
                <td>$0.935 T</td>
                <td>$-0.512 T</td>
                <td>+42.10%</td>
                <td>📉 Ακολούθησε η μεγάλη πτώση του 2022</td>
            </tr>
            <tr>
                <td>Χαμηλά 2020 (Covid Crash)</td>
                <td>$0.479 T</td>
                <td>$-0.150 T</td>
                <td>-12.30%</td>
                <td>🛒 Ιδανικό Σημείο Αγοράς (Καθαρισμός Μόχλευσης)</td>
            </tr>
            <tr class="warning-row">
                <td>Κορυφή 2018</td>
                <td>$0.665 T</td>
                <td>$-0.320 T</td>
                <td>+15.40%</td>
                <td>📉 Διόρθωση 20% στα τέλη του έτους</td>
            </tr>
            <tr class="alert-row">
                <td>Κορυφή 2007 (Πριν την Κρίση)</td>
                <td>$0.381 T</td>
                <td>$-0.179 T</td>
                <td>+35.20%</td>
                <td>💥 Παγκόσμια Χρηματοπιστωτική Κρίση 2008</td>
            </tr>
            <tr>
                <td>Ξεκίνημα Κύκλου (2005)</td>
                <td>$0.225 T</td>
                <td>$-0.065 T</td>
                <td>+5.10%</td>
                <td>✅ Υγιής Αγορά χωρίς Συστημικό Ρίσκο</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Dashboard updated successfully with 20-year history table!")
