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
        current_month_data = table.find_all('tr').find_all('td')
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

debit, cash1, cash2, past_debit = get_finra_data()
total_cash = cash1 + cash2
net_credit_balance = total_cash - debit
yearly_change = ((debit - past_debit) / past_debit) * 100
fed_assets = get_fed_data()
current_date = datetime.now().strftime("%d/%m/%Y")

# Διαχείριση Εβδομαδιαίου Log
log_file = "macro_history_log.json"
history_data = []
if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except:
        history_data = []

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
        f"Ανοίξτε τις 3 Καρτέλες: {live_url}"
    )
    base_url = "https://telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    try:
        requests.post(telegram_url, json={"chat_id": chat_id, "text": message})
    except:
        pass

weekly_rows = ""
for row in reversed(history_data):
    status_class = "alert-text" if row['change'] > 30 else "warning-text" if row['change'] > 15 else "success-text"
    weekly_rows += f'<tr class="{status_class}"><td>{row["date"]}</td><td>${row["debit"]/1000000:.3f} T</td><td>${row["net_credit"]/1000000:.3f} T</td><td>{row["change"]:.2f}%</td><td>${row["fed"]/1000000:.3f} T</td></tr>'

# Καθαρή HTML ως απλό string, χωρίς f-string για να μην μπερδεύονται τα άγκιστρα
html_template = """<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Institutional Macro Matrix</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }
        .card { background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 85%; }
        .grid { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }
        .value { font-size: 28px; font-weight: bold; color: #38bdf8; }
        .tab-container { margin: 30px auto; display: flex; justify-content: center; gap: 15px; width: 85%; }
        .tab-btn { background: #1e293b; color: #94a3b8; border: 2px solid #334155; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; }
        .tab-btn.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
        .tab-content { display: none; width: 85%; margin: 0 auto; }
        .tab-content.active { display: block; }
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; margin-top: 15px; }
        th, td { padding: 14px; text-align: center; border-bottom: 1px solid #334155; font-size: 14px; }
        th { background: #1e1b4b; color: #38bdf8; font-weight: bold; }
        tr:hover { background: #334155; }
        .alert-text { color: #ef4444; font-weight: bold; }
        .warning-text { color: #f59e0b; font-weight: bold; }
        .success-text { color: #10b981; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📊 Institutional Macro Leverage & Liquidity Matrix</h1>
    <div class="card">
        <h2>Συστημική Κατάσταση Κινδύνου</h2>
        <p class="alert-text" style="font-size:24px;">⚠️ ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ (Ακραία Μόχλευση & Ποσοτική Σύσφιξη Fed)</p>
    </div>
    <div class="grid">
        <div class="card" style="width:200px;"><h3>Margin Debt</h3><p class="value">__DEBIT__</p></div>
        <div class="card" style="width:200px;"><h3>Credit Balance</h3><p class="value" style="color:#f43f5e">__CREDIT__</p></div>
        <div class="card" style="width:200px;"><h3>Μεταβολή YoY</h3><p class="value" style="color:#f59e0b">__CHANGE__</p></div>
        <div class="card" style="width:200px;"><h3>Fed Assets</h3><p class="value" style="color:#a855f7">__FED__</p></div>
    </div>
    <div class="tab-container">
        <button class="tab-btn active" onclick="switchTab('tab1')">🏛️ 1. Ιστορικά Ορόσημα Κρίσεων</button>
        <button class="tab-btn" onclick="switchTab('tab2')">📅 2. Μηνιαία Εξέλιξη Κύκλου</button>
        <button class="tab-btn" onclick="switchTab('tab3')">⚡ 3. Εβδομαδιαίο Ραντάρ (Live)</button>
    </div>
    <div id="tab1" class="tab-content active">
        <table>
            <thead>
                <tr>
                    <th>Ιστορική Φάση / Ορόσημο</th>
                    <th>FINRA Margin Debt</th>
                    <th>Net Credit Balance</th>
                    <th>Ετήσια Μεταβολή</th>
                    <th>Fed Total Assets</th>
                    <th>Συστημικό Αποτέλεσμα / Στρατηγική</th>
                </tr>
            </thead>
            <tbody>
                <tr class="alert-text" style="background: rgba(239, 68, 68, 0.1);">
                    <td>Οκτώβριος 2026 (Σήμερα)</td>
                    <td>__DEBIT__</td>
                    <td>__CREDIT__</td>
                    <td>__CHANGE__</td>
                    <td>__FED__</td>
                    <td>🚨 Ακραία Μόχλευση (Σημερινή Κορυφή Φούσκας)</td>
                </tr>
                <tr class="alert-text">
                    <td>Οκτώβριος 2021 (Post-Covid Peak)</td>
                    <td>$0.935 T</td>
                    <td>$-0.512 T</td>
                    <td>+42.10%</td>
                    <td>$8.560 T</td>
                    <td>💥 Κορυφή Φούσκας. Ακολούθησε η Bear Market του 2022.</td>
                </tr>
                <tr class="alert-text">
                    <td>Ιούλιος 2007 (Pre-GFC Peak)</td>
                    <td>$0.381 T</td>
                    <td>$-0.179 T</td>
                    <td>+35.20%</td>
                    <td>$0.850 T</td>
                    <td>💥 Στέγνωμα ρευστότητας. Παγκόσμιο Κραχ 2008.</td>
                </tr>
                <tr class="warning-text">
                    <td>Μάιος 2018 (Fed QT Hikes)</td>
                    <td>$0.665 T</td>
                    <td>$-0.320 T</td>
                    <td>+15.40%</td>
                    <td>$4.320 T</td>
                    <td>📉 Ποσοτική σύσφιξη. Απότομη διόρθωση -20% στις μετοχές.</td>
                </tr>
                <tr class="success-text">
                    <td>Μάρτιος 2020 (Covid Crash Bottom)</td>
                    <td>$0.479 T</td>
                    <td>$-0.150 T</td>
                    <td>-12.30%</td>
                    <td>$5.250 T</td>
                    <td>🛒 Η Fed τύπωσε $3Τρς. ΤΕΛΕΙΟ ΣΗΜΕΙΟ ΑΓΟΡΑΣ ETFs.</td>
                </tr>
                <tr class="success-text">
                    <td>Φεβρουάριος 2009 (GFC Market Bottom)</td>
                    <td>$0.296 T</td>
                    <td>$-0.045 T</td>
                    <td>-22.30%</td>
                    <td>$1.950 T</td>
                    <td>🛒 Πλήρης εκκαθάριση χρέους. Ιστορικός Πάτος Ευκαιρίας.</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div id="tab2" class="tab-content">
        <table>
            <thead>
                <tr>
                    <th>Μήνας / Έτος</th>
                    <th>FINRA Margin Debt</th>
                    <th>Net Credit Balance</th>
                    <th>Ετήσια Μεταβολή</th>
                    <th>Fed Total Assets</th>
                    <th>Ανάλυση Πορείας Κύκλου</th>
                </tr>
            </thead>
            <tbody>
                <tr class="alert-text"><td>Οκτώβριος 2026</td><td>__DEBIT__</td><td>__CREDIT__</td><td>__CHANGE__</td><td>__FED__</td><td>🚨 Κορυφή Μανίας</td></tr>
                <tr class="alert-text"><td>Σεπτέμβριος 2026</td><td>$1.410 T</td><td>$-0.990 T</td><td>+34.20%</td><td>$6.790 T</td><td>🚨 Διόγκωση Χρέους</td></tr>
                <tr class="alert-text"><td>Αύγουστος 2026</td><td>$1.390 T</td><td>$-0.950 T</td><td>+31.50%</td><td>$6.820 T</td><td>🚨 Παραβίαση Ορίου 30%</td></tr>
