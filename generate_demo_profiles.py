import json
from datetime import datetime, timedelta
import random

def generate_transactions(start_date, months, income, expenses_profile):
    transactions = []
    
    # Generate 3 months of data
    for month_offset in range(months):
        # Determine the year and month
        current_date = start_date + timedelta(days=month_offset * 30)
        year = current_date.year
        month = current_date.month
        
        # 1. Salary / Income
        tarih_str = f"{year}-{month:02d}-05"
        transactions.append({
            "tarih": tarih_str,
            "aciklama": "MAAŞ ÖDEMESİ",
            "tutar": income,
            "is_income": True
        })
        
        # 2. Fixed Expenses (Rent/Bills)
        rent = expenses_profile.get("rent", 0)
        if rent > 0:
            transactions.append({
                "tarih": f"{year}-{month:02d}-06",
                "aciklama": "KİRA ÖDEMESİ",
                "tutar": rent,
                "is_income": False
            })
            
        bills = expenses_profile.get("bills", 0)
        if bills > 0:
            transactions.append({
                "tarih": f"{year}-{month:02d}-10",
                "aciklama": "ENERJİSA ELEKTRİK FATURASI",
                "tutar": bills * 0.4,
                "is_income": False
            })
            transactions.append({
                "tarih": f"{year}-{month:02d}-12",
                "aciklama": "İSKİ SU FATURASI",
                "tutar": bills * 0.2,
                "is_income": False
            })
            transactions.append({
                "tarih": f"{year}-{month:02d}-15",
                "aciklama": "TÜRK TELEKOM İNTERNET",
                "tutar": bills * 0.4,
                "is_income": False
            })
            
        # 3. Variable Expenses (Market, Yeme_Icme, Alisveris, Eglence)
        for category, amount in expenses_profile.get("variable", {}).items():
            num_transactions = max(2, int(amount / 500))  # Distribute over several transactions
            for i in range(num_transactions):
                day = random.randint(1, 28)
                tutar = round((amount / num_transactions) * random.uniform(0.8, 1.2), 2)
                
                # Pick appropriate dummy description based on category
                if category == "MARKET":
                    desc = random.choice(["MİGROS A.Ş.", "BİM BİRLEŞİK MAĞAZALAR", "CARREFOURSA", "ŞOK MARKET"])
                elif category == "YEME_ICME":
                    desc = random.choice(["STARBUCKS COFFEE", "YEMEKSEPETİ", "GETİR YEMEK", "NUSRET STEAKHOUSE", "BURGER KING"])
                elif category == "ALISVERIS":
                    desc = random.choice(["TRENDYOL", "HEPSİBURADA", "ZARA GİYİM", "BOYNER", "AMAZON TURKEY"])
                elif category == "EGLENCE":
                    desc = random.choice(["NETFLIX", "SPOTIFY", "BİLETİX", "STEAM GAMES", "APPLE COM BILL"])
                elif category == "ULASIM":
                    desc = random.choice(["UBER", "MARTI MOBILITE", "İSTANBULKART DOLUM", "PETROLOFİSİ"])
                else:
                    desc = "KART HARCAMASI"
                    
                transactions.append({
                    "tarih": f"{year}-{month:02d}-{day:02d}",
                    "aciklama": desc,
                    "tutar": tutar,
                    "is_income": False
                })
                
        # 4. Savings (Virman out to investment)
        savings = expenses_profile.get("savings", 0)
        if savings > 0:
            transactions.append({
                "tarih": f"{year}-{month:02d}-07",
                "aciklama": "YATIRIM HESABINA VİRMAN",
                "tutar": savings,
                "is_income": False
            })

    # Sort transactions by date
    transactions.sort(key=lambda x: x["tarih"])
    return transactions

def main():
    start_date = datetime(2026, 3, 1)
    months_of_data = 3
    
    profiles = {}
    
    # 1. Ahmet Bey — Yüksek Bütçe Riski
    # Income: 40,000. Spends: 48,000 (Overspending on Alışveriş and Eğlence)
    profiles["Ahmet_Bey"] = generate_transactions(
        start_date, months_of_data,
        income=40000,
        expenses_profile={
            "rent": 15000,
            "bills": 3000,
            "variable": {
                "MARKET": 4000,
                "YEME_ICME": 8000,
                "ALISVERIS": 12000,
                "EGLENCE": 4000,
                "ULASIM": 2000
            },
            "savings": 0
        }
    )
    
    # 2. Ayşe Hanım — Tasarrufçu Profil
    # Income: 50,000. Spends: 22,000. Saves: 25,000.
    profiles["Ayse_Hanim"] = generate_transactions(
        start_date, months_of_data,
        income=50000,
        expenses_profile={
            "rent": 12000,
            "bills": 2000,
            "variable": {
                "MARKET": 4000,
                "YEME_ICME": 1500,
                "ALISVERIS": 1000,
                "ULASIM": 1500
            },
            "savings": 25000
        }
    )
    
    # 3. Zeynep Hanım — Bütçeleme Yapmalı
    # Income: 35,000. Spends: 34,500. Not saving much, living paycheck to paycheck.
    profiles["Zeynep_Hanim"] = generate_transactions(
        start_date, months_of_data,
        income=35000,
        expenses_profile={
            "rent": 14000,
            "bills": 2500,
            "variable": {
                "MARKET": 6000,
                "YEME_ICME": 4000,
                "ALISVERIS": 5000,
                "ULASIM": 3000
            },
            "savings": 0
        }
    )
    
    # Save to JSON
    output_path = "c:\\Users\\sarat\\Desktop\\veri_seti\\demo_profiles.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)
        
    print(f"Generated 3 synthetic profiles successfully at {output_path}")

if __name__ == "__main__":
    main()
