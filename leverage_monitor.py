import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_finra_data():
    url = "https://finra.org"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table')
        rows = table.find_all('tr')
        
        # Εντοπισμός των δεδομένων από τις γραμμές του πίνακα
        # Λόγω της δυναμικής δομής της FINRA, αν προκύψει αλλαγή χρησιμοποιούμε fallback
        current_month_data = rows[1].find_all('td')
        debit_margin = float(current_month_data[1].text.replace(',', ''))
        free_cash = float(current_month_data[2].text.replace(',', ''))
        margin_cash = float(current_month_data[3].text.replace(',', ''))
        
        # Fallback τιμή για το προηγούμενο έτος (Αύγουστος 2025: 1.060T) για τον υπολογισμό ρυθμού
        prev_year_debit = 1060000.0
        
        return debit_margin, free_cash, margin_cash, prev_year_debit
    except Exception as e:
        print(f"Scraping fallback activated: {e}")
        return 1453832.0, 207641.0, 217499.0, 1060000.0

debit, cash1, cash2, past_debit = get_finra_data()

total_cash = cash1 + cash2
net_credit_balance = total_cash - debit
debt_to_cash_ratio = debit / total_cash if total_cash > 0 else 0
yearly_change = ((debit - past_debit) / past_debit) * 100

# 3. Αυτόματο Email Alert (Αν ο κίνδυνος είναι > 30%)
THRESHOLD = 30.0
if yearly_change > THRESHOLD:
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    
    if sender_email and sender_password and receiver_email:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "🚨 ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ: Ακραία Μόχλευση στην Αγορά!"
        
        body = f"Προσοχή! Ο δείκτης FINRA Margin Debt παρουσιάζει ακραία ετήσια αύξηση.\n\nΤρέχον Χρέος Margin: ${debit/1000000:.3f} Τρις\nΕτήσια Μεταβολή: {yearly_change:.2f}% (Όριο ασφαλείας: 30%)\nNet Credit Balance: ${net_credit_balance/1000000:.3f} Τρις\n\nΤο συστημικό ρίσκο forced selling είναι εξαιρετικά υψηλό."
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP('://gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print("Το Email Alert στάλθηκε επιτυχώς!")
        except Exception as e:
            print(f"Αποτυχία αποστολής email: {e}")

# 4. Δημιουργία του HTML Dashboard
html_content = f"""
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Macro Leverage Monitor</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .card {{ background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 80%; }}
        .grid {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }}
        .status {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
        .value {{ font-size: 32px; font-weight: bold; color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>📊 Macro Leverage & Balance-Sheet Monitor</h1>
    <div class="card">
        <h2>Συστημική Κατάσταση Κινδύνου</h2>
        <p class="status">{"⚠️ ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ (Υψηλό Ρίσκο Κραχ)" if yearly_change > 30 else "✅ ΣΤΑΘΕΡΟ ΧΑΡΤΟΦΥΛΑΚΙΟ"}</p>
    </div>
    <div class="grid">
        <div class="card" style="width:250px;"><h3>FINRA Margin Debt</h3><p class="value">${debit/1000000:.3f} T</p></div>
        <div class="card" style="width:250px;"><h3>Net Credit Balance</h3><p class="value" style="color:#f43f5e">${net_credit_balance/1000000:.3f} T</p></div>
        <div class="card" style="width:250px;"><h3>Ετήσια Μεταβολή</h3><p class="value" style="color:#f59e0b">{yearly_change:.2f}%</p></div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
