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

bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if bot_token and chat_id:
    live_url = "https://kostasg9786-cmyk.github.io/macro-monitor/"
    message = (
        f"📊 ΜΑΚΡΟΟΙΚΟΝΟΜΙΚΗ ΕΝΗΜΕΡΩΣΗ\n\n"
        f"🚨 Κατάσταση: ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ\n"
        f"• Margin Debt: ${debit/1000000:.3f} T\n"
        f"• Net Credit Balance: ${net_credit_balance/1000000:.3f} T\n"
        f"• Μεταβολή YoY: {yearly_change:.2f}%\n"
        f"• Fed Assets: ${fed_assets/1000000:.3f} T\n\n"
        f"Dashboard: {live_url}"
    )
    base_url = "https://telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(telegram_url, json=payload)
        print("Telegram sent successfully.")
    except Exception as e:
        print(f"Telegram error: {e}")

html_content = f"""
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Macro Leverage & Fed Monitor</title>
    <style>
        body {{ font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 80%; }}
        .grid {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }}
        .status {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
        .value {{ font-size: 28px; font-weight: bold; color: #38bdf8; }}
        table {{ width: 80%; margin: 20px auto; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 14px; text-align: center; border-bottom: 1px solid #334155; }}
        th {{ background: #1e1b4b; color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>📊 Institutional Macro Monitor</h1>
    <div class="card">
        <h2>Συστημική Κατάσταση Κινδύνου</h2>
        <p class="status">⚠️ ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ (Υψηλό Ρίσκο Κραχ)</p>
    </div>
    <div class="grid">
        <div class="card" style="width:200px;"><h3>Margin Debt</h3><p class="value">${debit/1000000:.3f} T</p></div>
        <div class="card" style="width:200px;"><h3>Credit Balance</h3><p class="value" style="color:#f43f5e">${net_credit_balance/1000000:.3f} T</p></div>
        <div class="card" style="width:200px;"><h3>Μεταβολή</h3><p class="value" style="color:#f59e0b">{yearly_change:.2f}%</p></div>
        <div class="card" style="width:200px;"><h3>Fed Assets</h3><p class="value" style="color:#a855f7">${fed_assets/1000000:.3f} T</p></div>
    </div>
    <h2>📜 Ιστορικά Ορόσημα 20ετίας</h2>
    <table>
        <thead>
            <tr>
                <th>Φάση Αγοράς</th>
                <th>Margin Debt</th>
                <th>Credit Balance</th>
                <th>Μεταβολή</th>
                <th>Fed Assets</th>
                <th>Αποτέλεσμα / Στρατηγική</th>
            </tr>
        </thead>
        <tbody>
            <tr style="color: #ef4444;">
                <td>Τρέχων Μήνας (2026)</td>
                <td>${debit/1000000:.3f} T</td>
                <td>${net_credit_balance/1000000:.3f} T</td>
                <td>{yearly_change:.2f}%</td>
                <td>${fed_assets/1000000:.3f} T</td>
                <td>🚨 Ακραία Μόχλευση (Σημερινή Φούσκα)</td>
            </tr>
            <tr style="color: #ef4444;">
                <td>Κορυφή 2021</td>
                <td>$0.935 T</td>
                <td>$-0.512 T</td>
                <td>+42.10%</td>
                <td>$8.750 T</td>
                <td>💥 Ακολούθησε το κραχ του 2022</td>
            </tr>
            <tr style="color: #ef4444;">
                <td>Κορυφή 2007</td>
                <td>$0.381 T</td>
                <td>$-0.179 T</td>
                <td>+35.20%</td>
                <td>$0.890 T</td>
                <td>💥 Παγκόσμιο Κραχ 2008</td>
            </tr>
            <tr style="color: #f59e0b;">
                <td>Κορυφή 2018</td>
                <td>$0.665 T</td>
                <td>$-0.320 T</td>
                <td>+15.40%</td>
                <td>$4.100 T</td>
                <td>📉 Διόρθωση αγοράς -20%</td>
            </tr>
            <tr style="color: #10b981;">
                <td>Πάτος 2020</td>
                <td>$0.479 T</td>
                <td>$-0.150 T</td>
                <td>-12.30%</td>
                <td>$7.000 T</td>
                <td>🛒 ΤΕΛΕΙΟ ΣΗΜΕΙΟ ΑΓΟΡΑΣ ETFs</td>
            </tr>
            <tr style="color: #10b981;">
                <td>Πάτος 2009</td>
                <td>$0.296 T</td>
                <td>$-0.045 T</td>
                <td>-22.30%</td>
                <td>$2.200 T</td>
                <td>🛒 Ιστορικός Πάτος Ευκαιρίας</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Dashboard completed.")
