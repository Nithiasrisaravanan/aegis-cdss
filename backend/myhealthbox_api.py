MEDICINES_DB = {
    "heart disease": [
        {
            "name": "Atorvastatin (Lipitor)",
            "agency": "FDA",
            "country": "USA/India",
            "code": "NDC-0071-0155",
            "leaflet_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2009/020702s056lbl.pdf",
            "stockists": ["Apollo Pharmacy", "MedPlus", "Tata 1mg", "Wellness Forever", "Aster Pharmacy"],
            "indian_brands": ["Atorva", "Storvas", "Lipicure", "Tonact", "Aztor"]
        },
        {
            "name": "Metoprolol (Lopressor)",
            "agency": "FDA",
            "country": "USA/India",
            "code": "NDC-0078-0478",
            "leaflet_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2008/019962s031lbl.pdf",
            "stockists": ["Apollo Pharmacy", "MedPlus", "Tata 1mg", "Netmeds", "PharmEasy"],
            "indian_brands": ["Metolar", "Seloken", "Metxl", "Betaloc", "Starpress"]
        },
        {
            "name": "Aspirin (Ecosprin)",
            "agency": "FDA",
            "country": "USA/India",
            "code": "NDC-0363-0486",
            "leaflet_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2010/020173s004lbl.pdf",
            "stockists": ["Apollo Pharmacy", "MedPlus", "Tata 1mg", "Wellness Forever", "Aster Pharmacy"],
            "indian_brands": ["Ecosprin", "Aspocid", "Colsprin", "Disprin", "Loprin"]
        }
    ],
    "no heart disease": [
        {
            "name": "Amlodipine (Norvasc)",
            "agency": "FDA",
            "country": "USA/India",
            "code": "NDC-0069-1520",
            "leaflet_url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2011/019787s040lbl.pdf",
            "stockists": ["Apollo Pharmacy", "MedPlus", "Tata 1mg", "Netmeds", "PharmEasy"],
            "indian_brands": ["Amlip", "Amlong", "Stamlo", "Amcard", "Norvasc"]
        }
    ]
}

STOCKIST_COORDS = {
    "Apollo Pharmacy":    {"lat": 13.0827, "lng": 80.2707, "city": "Chennai"},
    "MedPlus":            {"lat": 17.3850, "lng": 78.4867, "city": "Hyderabad"},
    "Tata 1mg":           {"lat": 28.6139, "lng": 77.2090, "city": "Delhi"},
    "Wellness Forever":   {"lat": 19.0760, "lng": 72.8777, "city": "Mumbai"},
    "Aster Pharmacy":     {"lat": 9.9312,  "lng": 76.2673, "city": "Kochi"},
    "Netmeds":            {"lat": 13.0827, "lng": 80.2707, "city": "Chennai"},
    "PharmEasy":          {"lat": 19.0760, "lng": 72.8777, "city": "Mumbai"}
}

def get_medicines(diagnosis_label: str) -> list:
    key = diagnosis_label.lower()
    for k in MEDICINES_DB:
        if k in key:
            return MEDICINES_DB[k]
    return MEDICINES_DB["heart disease"]

def get_stockist_coords(stockists: list) -> list:
    return [
        {**STOCKIST_COORDS[s], "name": s}
        for s in stockists if s in STOCKIST_COORDS
    ]

if __name__ == '__main__':
    meds = get_medicines("Heart Disease Present")
    for m in meds:
        print(f"\n{m['name']} | {m['agency']} | {m['code']}")
        print(f"  Stockists: {', '.join(m['stockists'])}")
        print(f"  Indian brands: {', '.join(m['indian_brands'])}")