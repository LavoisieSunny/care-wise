"""Indian Healthcare and Health Insurance Industry Constants."""

PROCEDURE_BENCHMARKS = {
    "angioplasty": {
        "name": "Coronary Angioplasty (PTCA with Stent)",
        "category": "Cardiology",
        "avg_stay_days": 3,
        "base_cost": 220000,
        "associated_medical_ratio": 0.55, # Doctor, OT, Anaesthesia, Nursing
        "consumables_ratio": 0.12,
        "urgency": "EMERGENCY"
    },
    "appendectomy": {
        "name": "Laparoscopic Appendectomy",
        "category": "General Surgery",
        "avg_stay_days": 2,
        "base_cost": 95000,
        "associated_medical_ratio": 0.50,
        "consumables_ratio": 0.10,
        "urgency": "URGENT"
    },
    "knee_replacement": {
        "name": "Total Knee Replacement (Unilateral)",
        "category": "Orthopedics",
        "avg_stay_days": 4,
        "base_cost": 260000,
        "associated_medical_ratio": 0.60,
        "consumables_ratio": 0.08,
        "urgency": "PLANNED"
    },
    "dengue_icu": {
        "name": "Severe Dengue / Sepsis ICU Management",
        "category": "Critical Care / General Medicine",
        "avg_stay_days": 5,
        "base_cost": 140000,
        "associated_medical_ratio": 0.50,
        "consumables_ratio": 0.15,
        "urgency": "EMERGENCY"
    },
    "fracture_fixation": {
        "name": "Emergency Trauma / Fracture Fixation",
        "category": "Orthopedics",
        "avg_stay_days": 3,
        "base_cost": 130000,
        "associated_medical_ratio": 0.52,
        "consumables_ratio": 0.11,
        "urgency": "URGENT"
    }
}

ROOM_TYPES = {
    "general": {
        "id": "general",
        "label": "General / Multi-Bed Ward",
        "tier": 1,
        "multiplier": 1.0
    },
    "twin_sharing": {
        "id": "twin_sharing",
        "label": "Twin Sharing Room",
        "tier": 2,
        "multiplier": 1.3
    },
    "single_private": {
        "id": "single_private",
        "label": "Single Private AC Room",
        "tier": 3,
        "multiplier": 1.7
    },
    "deluxe_suite": {
        "id": "deluxe_suite",
        "label": "Deluxe / Executive Suite",
        "tier": 4,
        "multiplier": 2.4
    }
}

RISK_TIERS = {
    "RECOMMENDED": {
        "label": "Recommended / Safe",
        "color": "#10B981",
        "description": "Within policy limits. 100% cashless coverage expected with minimal out-of-pocket expenses."
    },
    "FINANCIAL_RISK": {
        "label": "Financial Risk",
        "color": "#F59E0B",
        "description": "Room cap breached or high co-payment applies. Proportionate deduction penalty will increase caregiver out-of-pocket bills."
    },
    "NOT_ELIGIBLE": {
        "label": "Not Eligible for Cashless",
        "color": "#EF4444",
        "description": "Hospital is outside network or cashless denied. Requires upfront payment and retrospective reimbursement."
    }
}
