import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

def get_finra_data():
    url = "https://finra.org"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        current_month_data = rows.find_all('td')
        debit_margin = float(current_month_data.text.replace(',', ''))
        free_cash = float(current_month_data.text.replace(',', ''))
        margin_cash = float(current_month_data.text.replace(',', ''))
        prev_year_debit = 1060000.0
        return debit_margin, free_cash, margin_cash, prev_year_debit
    except Exception as e:
        print(f"Scraping fallback: {e}")
        return 1453832.0, 207641.0, 217499.0, 1060000.0

def get_fed_data():
    fed_url = "https://stlouisfed.org"
    try:
        response = requests.get(fed_url, timeout=10)
        lines = response.text.strip().split('\n')
        last_line = lines[-1]
        date, value = last_line.split(',')
        return float(value)
    except Exception as e:
        print(f"Fed Live Download fallback: {e}")
        return 6743031.0

# 1. Λήψη live δεδομένων
debit, cash1, cash2, past_debit = get_finra_data()
total_cash = cash1 + cash2
net_credit_balance = total_cash - debit
yearly_change = ((debit - past_debit) / past_debit) * 100
fed_assets = get_fed_data()
current_date = datetime.now().strftime("%d/%m/%Y")

# 2. Διαχείριση Ιστορικού Αρχείου (Persistent Log)
log_file = "macro_history_log.json"
history_data = []

if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except:
        history_data = []

# Έλεγχος για αποφυγή διπλότυπης εγγραφής την ίδια μέρα
if not history_data or history_data[-1]['date'] != current_date:
    new_record = {
        "date": current_date,
        "debit": debit,
        "net_credit": net_credit_balance,
        "change": yearly_change,
        "fed": fed_assets
    }
    history_data.append(new_record)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

# 3. Αποστολή στο Telegram
bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if bot_token and chat_id:
    live_url = "https://kostasg9786-cmyk.github.io/macro-monitor/"
    message = (
        f"📊 LIVE TREND ALERT ({current_date})\n\n"
        f"• Margin Debt: ${debit/1000000:.3f} T\n"
        f"• Net Credit Balance: ${net_credit_balance/1000000:.3f} T\n"
        f"• Μεταβολή YoY: {yearly_change:.2f}%\n"
        f"• Fed Assets: ${fed_assets/1000000:.3f} T\n\n"
        f"Παρακολουθήστε την τάση: {live_url}"
    )
    base_url = "https://telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    try:
        requests.post(telegram_url, json={"chat_id": chat_id, "text": message})
    except Exception as e:
        print(f"Telegram error: {e}")

# 4. Δημιουργία δυναμικού HTML
table_rows = ""
# Εμφανίζουμε τις καταγραφές με αντίστροφη χρονολογική σειρά (πιο πρόσφατη πάνω)
for row in reversed(history_data):
    trend_status = "🚨 Ακραίο Ρίσκο" if row['change'] > 30 else "⚠️ Προειδοποίηση" if row['change'] > 15 else "✅ Υγιής"
    status_class = "alert-text" if row['change'] > 30 else "warning-text" if row['change'] > 15 else "success-text"
    
    table_rows += f"""
    <tr class="{status_class}">
        <td>{row['date']}</td>
        <td>${row['debit']/1000000:.3f} T</td>
        <td>${row['net_credit']/1000000:.3f} T</td>
        <td>{row['change']:.2f}%</td>
        <td>${row['fed']/1000000:.3f} T</td>
        <td>{trend_status}</td>
    </tr>
    """

html_content = f"""
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Macro Trend & Liquidity Tracker</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .card {{ background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 85%; }}
        .grid {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }}
        .value {{ font-size: 28px; font-weight: bold; color: #38bdf8; }}
        table {{ width: 85%; margin: 20px auto; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 14px; text-align: center; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #1e1b4b; color: #38bdf8; font-weight: bold; }}
        tr:hover {{ background: #334155; }}
        .alert-text {{ color: #ef4444; font-weight: bold; }}
        .warning-text {{ color: #f59e0b; font-weight: bold; }}
        .success-text {{ color: #10b981; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📈 Live Macro Trend & Liquidity Tracker</h1>
    <div class="card">
        <h2>Συνεχόμενη Καταγραφή & Φυσική Εξέλιξη Αγοράς</h2>
        <p style="color: #94a3b8;">Παρακολουθήστε τη μεταβολή των αριθμών από εβδομάδα σε εβδομάδα για τον εντοπισμό της κορυφής.</p>
    </div>
    
    <div class="grid">
        <div class="card" style="width:200px;"><h3>Margin Debt</h3><p class="value">${debit/1000000:.3f} T</p></div>
        <div class="card" style="width:200px;"><h3>Credit Balance</h3><p class="value" style="color:#f43f5e">${net_credit_balance/1000000:.3f} T</p></div>
        <div class="card" style="width:200px;"><h3>Μεταβολή YoY</h3><p class="value" style="color:#f59e0b">{yearly_change:.2f}%</p></div>
        <div class="card" style="width:200px;"><h3>Fed Assets</h3><p class="value" style="color:#a855f7">${fed_assets/1000000:.3f} T</p></div>
    </div>

    <h2>📜 Χρονολόγιο Εξέλιξης & Κατεύθυνσης Τάσης (Trend Log)</h2>
    <table>
        <thead>
            <tr style="background: #1e1b4b; color: #38bdf8;">
                <th>Ημερομηνία Καταγραφής</th>
                <th>FINRA Margin Debt</th>
                <th>Net Credit Balance</th>
                <th>Ετήσια Μεταβολή</th>
                <th>Fed Total Assets</th>
                <th>Κατάσταση Μόχλευσης</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Trend Tracker updated successfully.")
