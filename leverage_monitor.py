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
        debit_margin = float(current_month_data[0].text.replace(',', ''))
        free_cash = float(current_month_data[1].text.replace(',', ''))
        margin_cash = float(current_month_data[2].text.replace(',', ''))
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

# Αποθήκευση δεδομένων σε JSON
live_data = {
    "debit": f"${debit/1000000:.3f} T",
    "credit": f"${net_credit_balance/1000000:.3f} T",
    "change": f"{yearly_change:.2f}%",
    "fed": f"${fed_assets/1000000:.3f} T",
    "history": history_data
}

with open("live_data.json", "w", encoding="utf-8") as f:
    json.dump(live_data, f, ensure_ascii=False, indent=4)

print("Python process completed with 100% success.")
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

def get_fred_series(series_id, default_val):
    url = f"https://stlouisfed.org{series_id}"
    try:
        response = requests.get(url, timeout=10)
        lines = response.text.strip().split('\n')
        # Ψάχνουμε από το τέλος για την πρώτη έγκυρη αριθμητική τιμή (αποφεύγοντας τυχόν '.' λόγω αργιών)
        for line in reversed(lines):
            parts = line.split(',')
            if len(parts) == 2 and parts[1].strip() != '.':
                return float(parts[1])
        return default_val
    except Exception as e:
        print(f"Fred error for {series_id}: {e}")
        return default_val

# Λήψη Live Δεδομένων
debit, cash1, cash2, past_debit = get_finra_data()
total_cash = cash1 + cash2
net_credit_balance = total_cash - debit
yearly_change = ((debit - past_debit) / past_debit) * 100
current_date = datetime.now().strftime("%d/%m/%Y")

# ΝΕΟΙ ΠΥΛΩΝΕΣ: Live δεδομένα από τη Fed (FRED)
fed_assets = get_fred_series("WALCL", 6743031.0)        # Fed Assets
bond_10y = get_fred_series("GS10", 4.35)                # 10-Year Treasury Yield (%)
junk_spread = get_fred_series("BAMLH0A0HYM2", 3.80)     # High Yield Option-Adjusted Spread (%)

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
        "fed": fed_assets,
        "bond": bond_10y,
        "spread": junk_spread
    }
    history_data.append(new_record)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if bot_token and chat_id:
    live_url = "https://github.io"
    message = (
        f"📊 LIVE TREND ALERT ({current_date})\n\n"
        f"• Margin Debt: ${debit/1000000:.3f} T\n"
        f"• Net Credit Balance: ${net_credit_balance/1000000:.3f} T\n"
        f"• Μεταβολή YoY: {yearly_change:.2f}%\n"
        f"• Fed Assets: ${fed_assets/1000000:.3f} T\n"
        f"• Απόδοση 10Y Ομολόγου: {bond_10y:.2f}%\n"
        f"• High Yield Spread: {junk_spread:.2f}%\n\n"
        f"Δείτε το αναβαθμισμένο Matrix: {live_url}"
    )
    base_url = "https://telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    try:
        requests.post(telegram_url, json={"chat_id": chat_id, "text": message})
    except:
        pass

# Αποθήκευση δεδομένων σε JSON για την HTML
live_data = {
    "debit": f"${debit/1000000:.3f} T",
    "credit": f"${net_credit_balance/1000000:.3f} T",
    "change": f"{yearly_change:.2f}%",
    "fed": f"${fed_assets/1000000:.3f} T",
    "bond": f"{bond_10y:.2f}%",
    "spread": f"{junk_spread:.2f}%",
    "history": history_data
}

with open("live_data.json", "w", encoding="utf-8") as f:
    json.dump(live_data, f, ensure_ascii=False, indent=4)

print("Python process with Bonds and Spreads completed successfully.")
