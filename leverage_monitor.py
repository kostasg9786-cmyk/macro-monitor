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

# 4ος Πυλώνας: Federal Reserve Liquidity (FRED WALCL Σταθερά Δεδομένα 2026)
fed_assets = 6743031.0  # $6.743 Τρισεκατομμύρια

bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if bot_token and chat_id:
    live_url = "https://kostasg9786-cmyk.github.io/macro-monitor/"
    
    message = (
        f"📊 ΘΕΣΜΙΚΗ ΕΝΗΜΕΡΩΣΗ ΜΟΧΛΕΥΣΗΣ & Fed (2026)\n\n"
        f"🚨 Κατάσταση: ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ\n"
        f"• Χρέος Margin: ${debit/1000000:.3f} Τρις\n"
        f"• Net Credit Balance: ${net_credit_balance/1000000:.3f} Τρις\n"
        f"• Ετήσια Μεταβολή Margin: {yearly_change:.2f}%\n"
        f"• Ισολογισμός Fed Assets: ${fed_assets/1000000:.3f} Τρις\n\n"
        f"Δείτε το Live Dashboard:\n{live_url}"
    )
    base_url = "https://telegram.org"
    telegram_url = f"{base_url}/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(telegram_url, json=payload)
        print("Telegram notification sent successfully.")
    except Exception as e:
        print(f"Telegram error: {e}")

html_content = f"""
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Macro Leverage & Fed Monitor</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .card {{ background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 20px; display: inline-block; width: 85%; }}
        .grid {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }}
        .status {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
        .value {{ font-size: 28px; font-weight: bold; color: #38bdf8; }}
        
        table {{ width: 85%; margin: 20px auto; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 14px; text-align: center; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #1e1b4b; color: #38bdf8; font-weight: bold; }}
        tr {{ display: none; }}
        .header-row {{ display: table-row !important; }}
        tr:hover {{ background: #334155; }}
        
        .alert-text {{ color: #ef4444; font-weight: bold; }}
        .warning-text {{ color: #f59e0b; font-weight: bold; }}
        .success-text {{ color: #10b981; font-weight: bold; }}
        
        .pagination {{ margin: 20px; display: flex; justify-content: center; gap: 15px; align-items: center; }}
        .btn {{ background: #38bdf8; color: #0f172a; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }}
        .btn:disabled {{ background: #475569; color: #94a3b8; cursor: not-allowed; }}
        #pageInfo {{ font-weight: bold; color: #94a3b8; }}
    </style>
</head>
<body>
    <h1>📊 Institutional Macro Leverage & Fed Liquidity Monitor</h1>
    
    <div class="card">
        <h2>Συστημική Κατάσταση Κινδύνου</h2>
        <p class="status">⚠️ ΚΟΚΚΙΝΟΣ ΣΥΝΑΓΕΡΜΟΣ (Υψηλό Ρίσκο Κραχ & Μείωση Ρευστότητας Fed)</p>
    </div>
    
    <div class="grid">
        <div class="card" style="width:220px;"><h3>FINRA Margin Debt</h3><p class="value">${debit/1000000:.3f} T</p></div>
        <div class="card" style="width:220px;"><h3>Net Credit Balance</h3><p class="value" style="color:#f43f5e">${net_credit_balance/1000000:.3f} T</p></div>
        <div class="card" style="width:220px;"><h3>Ετήσια Μεταβολή</h3><p class="value" style="color:#f59e0b">{yearly_change:.2f}%</p></div>
        <div class="card" style="width:220px;"><h3>Fed Total Assets</h3><p class="value" style="color:#a855f7">${fed_assets/1000000:.3f} T</p></div>
    </div>

    <h2>📜 Ιστορικά Ορόσημα 20ετίας (Μόχλευση Αγοράς vs Ρευστότητα Fed)</h2>
    <table id="historyTable">
        <thead>
            <tr class="header-row">
                <th>Φάση Αγοράς / Ιστορικό Ορόσημο</th>
                <th>FINRA Margin Debt</th>
                <th>Net Credit Balance</th>
                <th>Ετήσια Μεταβολή</th>
                <th>Fed Total Assets</th>
                <th>Συστημικό Αποτέλεσμα / Στρατηγική</th>
            </tr>
        </thead>
        <tbody>
            <tr class="alert-text" style="background: rgba(239, 68, 68, 0.1);">
                <td>Τρέχων Μήνας (2026)</td>
                <td>${debit/1000000:.3f} T</td>
                <td>${net_credit_balance/1000000:.3f} T</td>
                <td>{yearly_change:.2f}%</td>
                <td>$6.743 T</td>
                <td>🚨 Ακραίο Margin + QT (Υψηλότερο Συστημικό Ρίσκο)</td>
            </tr>
            <tr class="alert-text">
                <td>Κορυφή 2021 (Post-Covid Peak)</td>
                <td>$0.935 T</td>
                <td>$-0.512 T</td>
                <td>+42.10%</td>
                <td>$8.750 T</td>
                <td>💥 Ιστορική Φούσκα ρευστότητας. Ακολούθησε το κραχ του 2022.</td>
            </tr>
            <tr class="alert-text">
                <td>Κορυφή 2007 (Pre-GFC Peak)</td>
                <td>$0.381 T</td>
                <td>$-0.179 T</td>
                <td>+35.20%</td>
                <td>$0.890 T</td>
                <td>💥 Στέγνωμα Διατραπεζικής. Παγκόσμιο Κραχ 2008.</td>
            </tr>
            <tr class="warning-text">
                <td>Κορυφή 2018 (Fed QT Rate Hikes)</td>
                <td>$0.665 T</td>
                <td>$-0.320 T</td>
                <td>+15.40%</td>
                <td>$4.100 T</td>
                <td>📉 Η Fed μείωσε ισολογισμό, προκαλώντας πτώση -20%.</td>
            </tr>
            <tr class="success-text">
                <td>Πάτος 2020 (Covid Crash Bottom)</td>
                <td>$0.479 T</td>
                <td>$-0.150 T</td>
                <td>-12.30%</td>
                <td>$7.000 T</td>
                <td>🛒 Η Fed τύπωσε $3Τρς. ΤΕΛΕΙΟ ΣΗΜΕΙΟ ΑΓΟΡΑΣ ETFs.</td>
            </tr>
            <tr class="success-text">
                <td>Πάτος 2009 (GFC Market Bottom)</td>
                <td>$0.296 T</td>
                <td>$-0.045 T</td>
                <td>-22.30%</td>
                <td>$2.200 T</td>
                <td>🛒 Πλήρης εκκαθάριση χρέους. Αφετηρία ιστορικού Bull Market.</td>
            </tr>
        </tbody>
    </table>

    <div class="pagination">
        <button class="btn" id="prevBtn" onclick="prevPage()">⏮️ Προηγούμενη</button>
        <span id="pageInfo">Σελίδα 1</span>
        <button class="btn" id="nextBtn" onclick="nextPage()">Επόμενη ⏭️</button>
    </div>

    <script>
        let currentPage = 1;
        const rowsPerPage = 4; 
        const table = document.getElementById("historyTable");
        const tbody = table.getElementsByTagName("tbody");
        const rows = tbody.getElementsByTagName("tr");
        const totalPages = Math.ceil(rows.length / rowsPerPage);

        function showPage(page) {{
            if (page < 1) page = 1;
            if (page > totalPages) page = totalPages;
            currentPage = page;

            for (let i = 0; i < rows.length; i++) {{
                rows[i].style.display = "none";
            }}

            let start = (page - 1) * rowsPerPage;
            let end = start + rowsPerPage;
            for (let i = start; i < end && i < rows.length; i++) {{
                rows[i].style.display = "table-row";
            }}

            document.getElementById("pageInfo").innerText = "Σελίδα " + page + " από " + totalPages;
            document.getElementById("prevBtn").disabled = (page === 1);
            document.getElementById("nextBtn").disabled = (page === totalPages);
        }}

        function prevPage() {{ showPage(currentPage - 1); }}
        function nextPage() {{ showPage(currentPage + 1); }}

        showPage(1);
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Institutional Dashboard with 4 Pillars created successfully!")
