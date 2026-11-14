"""Curated pharmacological knowledge base for PharmaGuard AI.

This is a *demonstration* knowledge base, not a validated clinical database.
Rules are curated from FDA-approved prescribing information, RxNorm-style
generic/brand naming, and standard pharmacology references covering CYP450
metabolism, pharmacodynamic synergy, renal clearance, and GI chelation.

Design principle: fail closed. A medication that is not in the registry must be
surfaced as UNVERIFIED rather than silently treated as safe.
"""

from typing import Any, Dict, List

KNOWLEDGE_BASE_VERSION = "2.0"
KNOWLEDGE_BASE_UPDATED = "2026-11-14"

DISCLAIMER = (
    "Educational demonstration only. This knowledge base is a curated subset and "
    "is not a substitute for a validated clinical interaction database, pharmacist "
    "review, or professional medical judgment."
)


def _drug(
    name: str,
    brand: str,
    drug_class: str,
    dose: str,
    default_time: str,
    cyp: str,
    food: str,
    aliases: List[str],
    *,
    doses_per_day: int = 1,
    frequency: str = "daily",
    meal_relation: str = "any",
    preferred_period: str = "any",
    min_interval_hours: float = 20,
    schedule_note: str = "",
) -> Dict[str, Any]:
    """Builds a registry entry with the metadata the scheduler needs."""
    return {
        "name": name,
        "brand": brand,
        "class": drug_class,
        "default_dose": dose,
        "default_time": default_time,
        "cyp_pathway": cyp,
        "food_warnings": food,
        "aliases": aliases,
        "schedule": {
            "doses_per_day": doses_per_day,
            "frequency": frequency,
            "meal_relation": meal_relation,
            "preferred_period": preferred_period,
            "min_interval_hours": min_interval_hours,
            "note": schedule_note,
        },
    }


# ---------------------------------------------------------------------------
# Drug registry
# ---------------------------------------------------------------------------
# Keys are canonical snake_case identifiers. Aliases are matched as whole
# tokens, so short strings such as "iron" can never match "spironolactone".
DRUG_REGISTRY: Dict[str, Dict[str, Any]] = {
    # --- Anticoagulants / antiplatelets -----------------------------------
    "warfarin": _drug(
        "Warfarin", "Coumadin / Jantoven", "Anticoagulant (Vitamin K antagonist)",
        "5 mg", "Evening", "CYP2C9 (major), CYP3A4",
        "Keep vitamin K intake consistent; avoid large changes in green vegetables.",
        ["coumadin", "jantoven", "warfarin sodium"],
        preferred_period="evening",
        schedule_note="Take at the same time each evening.",
    ),
    "aspirin": _drug(
        "Aspirin", "Bayer / Ecotrin", "Antiplatelet / Salicylate",
        "81 mg", "Morning", "Renal / hepatic",
        "Take with food to reduce stomach irritation.",
        ["bayer", "ecotrin", "acetylsalicylic acid", "asa"],
        meal_relation="with_meal", preferred_period="morning",
        schedule_note="Take with food.",
    ),
    "clopidogrel": _drug(
        "Clopidogrel", "Plavix", "Antiplatelet (P2Y12 inhibitor)",
        "75 mg", "Morning", "CYP2C19 (activation)",
        "May be taken with or without food.",
        ["plavix"],
        preferred_period="morning",
    ),
    # --- Statins / fibrates ------------------------------------------------
    "simvastatin": _drug(
        "Simvastatin", "Zocor", "HMG-CoA reductase inhibitor (statin)",
        "20 mg", "Bedtime", "CYP3A4 substrate",
        "Avoid grapefruit and grapefruit juice.",
        ["zocor"],
        preferred_period="bedtime",
        schedule_note="Take in the evening; cholesterol synthesis peaks overnight.",
    ),
    "atorvastatin": _drug(
        "Atorvastatin", "Lipitor", "HMG-CoA reductase inhibitor (statin)",
        "20 mg", "Evening", "CYP3A4 substrate",
        "Avoid large amounts of grapefruit juice.",
        ["lipitor"],
        preferred_period="evening",
    ),
    "gemfibrozil": _drug(
        "Gemfibrozil", "Lopid", "Fibrate",
        "600 mg", "Morning & Evening", "Renal / hepatic",
        "Take 30 minutes before meals.",
        ["lopid"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    # --- Antibiotics / antifungals ----------------------------------------
    "clarithromycin": _drug(
        "Clarithromycin", "Biaxin", "Macrolide antibiotic",
        "500 mg", "Morning & Evening", "Potent CYP3A4 inhibitor",
        "May be taken with or without food.",
        ["biaxin"],
        doses_per_day=2, frequency="bid", min_interval_hours=10,
        schedule_note="Complete the full antibiotic course.",
    ),
    "azithromycin": _drug(
        "Azithromycin", "Zithromax / Z-Pak", "Macrolide antibiotic",
        "250 mg", "Morning", "Mild CYP3A4 inhibitor; QT prolongation",
        "May be taken with or without food.",
        ["zithromax", "z-pak", "zpak"],
        preferred_period="morning",
    ),
    "ciprofloxacin": _drug(
        "Ciprofloxacin", "Cipro", "Fluoroquinolone antibiotic",
        "500 mg", "Morning & Evening", "CYP1A2 inhibitor",
        "Separate from dairy, calcium, iron, and antacids by at least 2 hours.",
        ["cipro"],
        doses_per_day=2, frequency="bid", min_interval_hours=10,
        schedule_note="Keep 2 hours away from dairy, calcium, iron, and antacids.",
    ),
    "levofloxacin": _drug(
        "Levofloxacin", "Levaquin", "Fluoroquinolone antibiotic",
        "500 mg", "Morning", "Renal elimination",
        "Separate from calcium, iron, and antacids.",
        ["levaquin"],
        preferred_period="morning",
        schedule_note="Keep 2 hours away from minerals and antacids.",
    ),
    "metronidazole": _drug(
        "Metronidazole", "Flagyl", "Nitroimidazole antibiotic",
        "500 mg", "Morning & Evening", "CYP2C9 inhibitor",
        "Avoid alcohol during and for 3 days after treatment.",
        ["flagyl"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    "trimethoprim_sulfamethoxazole": _drug(
        "Trimethoprim-Sulfamethoxazole", "Bactrim / Septra", "Sulfonamide antibiotic",
        "160/800 mg", "Morning & Evening", "CYP2C9 inhibitor; renal tubular effects",
        "Drink plenty of water; take with food.",
        ["bactrim", "septra", "tmp-smx", "tmp smx", "trimethoprim sulfamethoxazole",
         "co-trimoxazole", "cotrimoxazole"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    "fluconazole": _drug(
        "Fluconazole", "Diflucan", "Azole antifungal",
        "150 mg", "Morning", "CYP2C9 / CYP3A4 inhibitor",
        "May be taken with or without food.",
        ["diflucan"],
        preferred_period="morning",
    ),
    "itraconazole": _drug(
        "Itraconazole", "Sporanox", "Azole antifungal",
        "200 mg", "Morning", "Potent CYP3A4 inhibitor",
        "Take with a full meal for absorption.",
        ["sporanox"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    # --- Analgesics / NSAIDs ----------------------------------------------
    "ibuprofen": _drug(
        "Ibuprofen", "Advil / Motrin", "NSAID",
        "400 mg", "Morning, Midday & Evening", "CYP2C9 inhibitor",
        "Take with food or milk to reduce stomach irritation.",
        ["advil", "motrin", "brufen"],
        doses_per_day=3, frequency="tid", meal_relation="with_meal",
        min_interval_hours=4,
        schedule_note="Use the lowest effective dose for the shortest time.",
    ),
    "naproxen": _drug(
        "Naproxen", "Aleve / Naprosyn", "NSAID",
        "250 mg", "Morning & Evening", "CYP2C9 inhibitor",
        "Take with food or milk.",
        ["aleve", "naprosyn"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    "acetaminophen": _drug(
        "Acetaminophen", "Tylenol", "Analgesic / Antipyretic",
        "500 mg", "As needed", "Hepatic",
        "Do not exceed 3,000 mg per day; avoid alcohol.",
        ["tylenol", "paracetamol"],
        frequency="as_needed", min_interval_hours=6,
        schedule_note="Maximum 3,000 mg per day for this demo.",
    ),
    # --- GI -----------------------------------------------------------------
    "omeprazole": _drug(
        "Omeprazole", "Prilosec", "Proton pump inhibitor",
        "20 mg", "Morning (fasting)", "CYP2C19 inhibitor",
        "Take 30-60 minutes before breakfast.",
        ["prilosec"],
        meal_relation="fasting", preferred_period="morning",
        schedule_note="Take before the first meal of the day.",
    ),
    "pantoprazole": _drug(
        "Pantoprazole", "Protonix", "Proton pump inhibitor",
        "40 mg", "Morning (fasting)", "CYP2C19 (weak)",
        "Take 30-60 minutes before breakfast.",
        ["protonix"],
        meal_relation="fasting", preferred_period="morning",
    ),
    # --- Cardiovascular -----------------------------------------------------
    "lisinopril": _drug(
        "Lisinopril", "Prinivil / Zestril", "ACE inhibitor",
        "10 mg", "Morning", "Renal elimination",
        "Avoid potassium-based salt substitutes.",
        ["prinivil", "zestril"],
        preferred_period="morning",
    ),
    "losartan": _drug(
        "Losartan", "Cozaar", "Angiotensin II receptor blocker (ARB)",
        "50 mg", "Morning", "CYP2C9 / CYP3A4",
        "Avoid potassium-based salt substitutes.",
        ["cozaar"],
        preferred_period="morning",
    ),
    "spironolactone": _drug(
        "Spironolactone", "Aldactone", "Potassium-sparing diuretic",
        "25 mg", "Morning", "Renal / hepatic",
        "Avoid high-potassium foods and salt substitutes.",
        ["aldactone"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    "furosemide": _drug(
        "Furosemide", "Lasix", "Loop diuretic",
        "40 mg", "Morning", "Renal elimination",
        "Take in the morning to avoid nighttime urination.",
        ["lasix"],
        preferred_period="morning",
    ),
    "hydrochlorothiazide": _drug(
        "Hydrochlorothiazide", "Microzide / HydroDIURIL", "Thiazide diuretic",
        "25 mg", "Morning", "Renal elimination",
        "Take in the morning; monitor potassium.",
        ["hctz", "microzide", "hydrodiuril"],
        preferred_period="morning",
    ),
    "amlodipine": _drug(
        "Amlodipine", "Norvasc", "Calcium channel blocker",
        "5 mg", "Morning", "CYP3A4 substrate",
        "May be taken with or without food.",
        ["norvasc"],
        preferred_period="morning",
    ),
    "metoprolol": _drug(
        "Metoprolol", "Toprol-XL / Lopressor", "Beta blocker",
        "50 mg", "Morning & Evening", "CYP2D6 substrate",
        "Take with or just after a meal; do not stop abruptly.",
        ["toprol", "toprol-xl", "lopressor"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    "verapamil": _drug(
        "Verapamil", "Calan / Isoptin", "Calcium channel blocker",
        "80 mg", "Morning, Midday & Evening", "CYP3A4 substrate",
        "Take with food; avoid grapefruit juice.",
        ["calan", "isoptin"],
        doses_per_day=3, frequency="tid", meal_relation="with_meal",
        min_interval_hours=4,
    ),
    "digoxin": _drug(
        "Digoxin", "Lanoxin", "Cardiac glycoside",
        "0.125 mg", "Morning", "Renal elimination",
        "Take at the same time each day; monitor potassium.",
        ["lanoxin"],
        preferred_period="morning",
    ),
    "amiodarone": _drug(
        "Amiodarone", "Cordarone / Pacerone", "Antiarrhythmic",
        "200 mg", "Morning", "CYP2C9 / CYP3A4 inhibitor",
        "Take consistently with regard to food; avoid grapefruit.",
        ["cordarone", "pacerone"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    # --- Endocrine / metabolic ---------------------------------------------
    "metformin": _drug(
        "Metformin", "Glucophage / Fortamet", "Biguanide antidiabetic",
        "500 mg", "Morning & Evening", "Renal elimination",
        "Take with meals to reduce stomach upset.",
        ["glucophage", "fortamet"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    "glipizide": _drug(
        "Glipizide", "Glucotrol", "Sulfonylurea",
        "5 mg", "Morning (fasting)", "CYP2C9 substrate",
        "Take 30 minutes before breakfast; watch for low blood sugar.",
        ["glucotrol"],
        meal_relation="fasting", preferred_period="morning",
    ),
    "insulin": _drug(
        "Insulin", "Basaglar / Humalog", "Insulin",
        "10 units", "With meals", "Not CYP-mediated",
        "Individualized dosing; rotate injection sites; monitor glucose.",
        ["basaglar", "humalog", "lantus", "novolog"],
        frequency="as_needed",
        schedule_note="Individualized regimen; not auto-scheduled in this demo.",
    ),
    "levothyroxine": _drug(
        "Levothyroxine", "Synthroid / Levoxyl / Euthyrox", "Thyroid hormone (T4)",
        "75 mcg", "Early morning (fasting)", "Hepatic / renal",
        "Take 30-60 minutes before breakfast with water.",
        ["synthroid", "levoxyl", "euthyrox", "t4", "l-thyroxine"],
        meal_relation="fasting", preferred_period="morning",
        schedule_note="Take fasting, 30-60 minutes before breakfast.",
    ),
    # --- Psychiatry / pain --------------------------------------------------
    "sertraline": _drug(
        "Sertraline", "Zoloft", "SSRI antidepressant",
        "50 mg", "Morning", "CYP2D6 / CYP3A4",
        "May be taken with or without food.",
        ["zoloft"],
        preferred_period="morning",
    ),
    "fluoxetine": _drug(
        "Fluoxetine", "Prozac", "SSRI antidepressant",
        "20 mg", "Morning", "CYP2D6 inhibitor",
        "Take in the morning to reduce insomnia.",
        ["prozac"],
        preferred_period="morning",
    ),
    "citalopram": _drug(
        "Citalopram", "Celexa", "SSRI antidepressant",
        "20 mg", "Morning", "CYP2C19 / CYP3A4",
        "May be taken with or without food; QT caution.",
        ["celexa"],
        preferred_period="morning",
    ),
    "tramadol": _drug(
        "Tramadol", "Ultram", "Opioid analgesic / serotonergic",
        "50 mg", "As needed", "CYP2D6 / CYP3A4",
        "May cause dizziness; avoid alcohol.",
        ["ultram"],
        frequency="as_needed", min_interval_hours=6,
        schedule_note="As-needed pain medicine; not auto-scheduled.",
    ),
    "linezolid": _drug(
        "Linezolid", "Zyvox", "Oxazolidinone antibiotic / MAO inhibitor",
        "600 mg", "Morning & Evening", "Non-selective MAO inhibition",
        "Avoid tyramine-rich foods; serotonin syndrome risk.",
        ["zyvox"],
        doses_per_day=2, frequency="bid", min_interval_hours=10,
    ),
    "lithium": _drug(
        "Lithium", "Lithobid", "Mood stabilizer",
        "300 mg", "Morning & Evening", "Renal elimination",
        "Maintain consistent salt and fluid intake; monitor levels.",
        ["lithobid", "lithium carbonate"],
        doses_per_day=2, frequency="bid", meal_relation="with_meal",
        min_interval_hours=10,
    ),
    # --- Rheumatology / immunology -----------------------------------------
    "methotrexate": _drug(
        "Methotrexate", "Trexall / Rheumatrex", "Antimetabolite / immunosuppressant",
        "15 mg", "Weekly (same day)", "Renal clearance",
        "Take exactly as prescribed; folic acid is usually co-prescribed.",
        ["trexall", "rheumatrex"],
        frequency="weekly", meal_relation="any", preferred_period="morning",
        schedule_note="WEEKLY dosing - never take daily. Confirm the day with your prescriber.",
    ),
    "allopurinol": _drug(
        "Allopurinol", "Zyloprim", "Xanthine oxidase inhibitor",
        "100 mg", "Morning", "Renal elimination",
        "Take after a meal; drink plenty of water.",
        ["zyloprim"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    "azathioprine": _drug(
        "Azathioprine", "Imuran", "Immunosuppressant",
        "50 mg", "Morning", "TPMT / xanthine oxidase metabolism",
        "Take with food; report fever or unusual bruising.",
        ["imuran"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    # --- Minerals / electrolytes -------------------------------------------
    "ferrous_sulfate": _drug(
        "Ferrous Sulfate (Iron)", "Feosol / Slow Fe", "Mineral supplement",
        "325 mg", "Midday", "None (divalent cation)",
        "Vitamin C improves absorption; calcium, tea, and antacids reduce it.",
        ["iron", "feosol", "slow fe", "ferrous sulfate", "ferrous"],
        preferred_period="midday",
        schedule_note="Keep 4 hours away from levothyroxine and antacids.",
    ),
    "calcium_carbonate": _drug(
        "Calcium Carbonate", "Tums / Caltrate", "Mineral supplement / antacid",
        "600 mg", "With meals", "None (polyvalent cation)",
        "Take with meals; separate from antibiotics and thyroid hormone.",
        ["calcium", "tums", "caltrate", "calcium carbonate"],
        meal_relation="with_meal", preferred_period="midday",
        schedule_note="Keep 3-4 hours away from ciprofloxacin/levofloxacin and levothyroxine.",
    ),
    "potassium_chloride": _drug(
        "Potassium Chloride", "K-Dur / Klor-Con", "Electrolyte supplement",
        "20 mEq", "With meals", "Renal excretion",
        "Take with a full glass of water and food.",
        ["potassium", "k-dur", "klor-con", "potassium chloride"],
        meal_relation="with_meal", preferred_period="morning",
    ),
    # --- Other --------------------------------------------------------------
    "sildenafil": _drug(
        "Sildenafil", "Viagra / Revatio", "PDE5 inhibitor",
        "50 mg", "As needed", "CYP3A4 substrate",
        "Do not combine with nitrates. Avoid heavy meals before use.",
        ["viagra", "revatio"],
        frequency="as_needed", min_interval_hours=24,
        schedule_note="As-needed; never combine with nitrates.",
    ),
    "nitroglycerin": _drug(
        "Nitroglycerin", "Nitrostat", "Nitrate vasodilator",
        "0.4 mg", "As needed", "Hepatic",
        "Sit down before use; do not combine with PDE5 inhibitors.",
        ["nitrostat", "glyceryl trinitrate", "gtn"],
        frequency="as_needed", min_interval_hours=5,
        schedule_note="As-needed chest pain medicine.",
    ),
    "ondansetron": _drug(
        "Ondansetron", "Zofran", "5-HT3 antagonist antiemetic",
        "4 mg", "As needed", "CYP3A4 / CYP2D6",
        "May cause QT prolongation; avoid in severe electrolyte imbalance.",
        ["zofran"],
        frequency="as_needed", min_interval_hours=8,
        schedule_note="As-needed nausea medicine.",
    ),
    "phenytoin": _drug(
        "Phenytoin", "Dilantin", "Antiepileptic",
        "100 mg", "Morning, Midday & Evening", "CYP2C9 substrate / inducer",
        "Take with food; do not stop abruptly.",
        ["dilantin"],
        doses_per_day=3, frequency="tid", meal_relation="with_meal",
        min_interval_hours=4,
    ),
    "rifampin": _drug(
        "Rifampin", "Rifadin", "Antimycobacterial / CYP inducer",
        "600 mg", "Morning (fasting)", "Potent CYP3A4 / CYP2C9 inducer",
        "Take on an empty stomach; may turn urine orange.",
        ["rifadin", "rifampicin"],
        meal_relation="fasting", preferred_period="morning",
    ),
    "tizanidine": _drug(
        "Tizanidine", "Zanaflex", "Central alpha-2 agonist muscle relaxant",
        "4 mg", "Bedtime", "CYP1A2 substrate",
        "May cause drowsiness; avoid alcohol.",
        ["zanaflex"],
        preferred_period="bedtime",
    ),
    "iodinated_contrast": _drug(
        "Iodinated Contrast", "Iodinated contrast media", "Diagnostic contrast agent",
        "1 procedure", "Procedure", "Renal elimination",
        "Notify the care team of kidney disease, metformin use, or prior reactions.",
        ["contrast", "contrast dye", "iodinated contrast", "ct contrast", "mri contrast"],
        frequency="as_needed",
        schedule_note="Procedure-only agent; not a daily medication.",
    ),
}


# ---------------------------------------------------------------------------
# Pairwise interaction rules
# ---------------------------------------------------------------------------
def _rule(
    a: str,
    b: str,
    severity: str,
    title: str,
    mechanism: str,
    action: str,
    category: str,
    *,
    spacing: bool = False,
    hours: float = 0,
    source: str = "FDA-approved labeling and standard pharmacology references",
) -> Dict[str, Any]:
    return {
        "pair": (a, b),
        "severity": severity,
        "title": title,
        "mechanism": mechanism,
        "clinical_action": action,
        "category": category,
        "spacing_resolvable": spacing,
        "recommended_spacing_hours": hours,
        "source": source,
    }


INTERACTION_RULES: List[Dict[str, Any]] = [
    # --- Bleeding / anticoagulation ---------------------------------------
    _rule(
        "warfarin", "ibuprofen", "CRITICAL",
        "Severe Synergistic Bleeding & GI Mucosal Hemorrhage",
        "NSAIDs inhibit platelet COX-1 and irritate the gastric mucosa while warfarin "
        "impairs clotting-factor synthesis. Together they sharply increase major GI bleeding.",
        "Avoid the combination. Use acetaminophen for mild pain where appropriate, or add "
        "gastroprotection only under clinician direction.",
        "pharmacodynamic",
    ),
    _rule(
        "warfarin", "naproxen", "CRITICAL",
        "Severe Synergistic Bleeding & GI Mucosal Hemorrhage",
        "Naproxen inhibits platelet aggregation and causes gastric mucosal injury while "
        "warfarin impairs clotting-factor synthesis.",
        "Avoid the combination. Consider acetaminophen or a non-NSAID alternative after "
        "clinician review.",
        "pharmacodynamic",
    ),
    _rule(
        "warfarin", "aspirin", "CRITICAL",
        "Dual Antiplatelet & Anticoagulant Hemorrhagic Synergy",
        "Combined inhibition of platelet plug formation and the coagulation cascade "
        "dramatically raises major bleeding risk.",
        "Only use with a documented cardiology indication (e.g. recent stent). Otherwise "
        "deprescribe after clinician review; monitor for bleeding.",
        "pharmacodynamic",
    ),
    _rule(
        "aspirin", "ibuprofen", "MODERATE",
        "NSAID Interference With Aspirin Cardioprotection & GI Risk",
        "Ibuprofen can competitively block aspirin's irreversible platelet inhibition and "
        "adds gastric mucosal injury.",
        "Take aspirin at least 2 hours before ibuprofen, or use acetaminophen. Discuss "
        "cardioprotection with the prescriber.",
        "pharmacodynamic", spacing=True, hours=2,
    ),
    # --- Warfarin metabolic interactions ---------------------------------
    _rule(
        "warfarin", "amiodarone", "CRITICAL",
        "CYP2C9 Inhibition & Severe INR Elevation",
        "Amiodarone inhibits CYP2C9 and CYP3A4, reducing warfarin clearance and causing "
        "marked INR elevation that can persist for weeks.",
        "Reduce the warfarin dose pre-emptively per protocol and check INR within 3-5 days "
        "and weekly thereafter.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "metronidazole", "CRITICAL",
        "CYP2C9 Inhibition & INR Elevation",
        "Metronidazole inhibits CYP2C9, reducing warfarin metabolism and increasing "
        "bleeding risk.",
        "Check INR within 3-5 days; anticipate a warfarin dose reduction.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "fluconazole", "CRITICAL",
        "CYP2C9 Inhibition & INR Elevation",
        "Fluconazole is a potent CYP2C9 inhibitor that can substantially raise warfarin "
        "exposure and INR.",
        "Monitor INR closely and reduce the warfarin dose per protocol.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "trimethoprim_sulfamethoxazole", "CRITICAL",
        "CYP2C9 Inhibition, Protein-Binding Displacement & INR Spike",
        "TMP-SMX inhibits CYP2C9 and displaces warfarin from albumin, producing a rapid "
        "and clinically significant INR increase.",
        "Use an alternative antibiotic when possible; otherwise check INR within 3 days "
        "and reduce the warfarin dose per protocol.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "clarithromycin", "MODERATE",
        "Macrolide Potentiation of Warfarin",
        "Clarithromycin inhibits CYP3A4 and may increase warfarin exposure and INR.",
        "Monitor INR during and after the antibiotic course.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "ciprofloxacin", "MODERATE",
        "Fluoroquinolone Potentiation of Warfarin",
        "Ciprofloxacin can increase warfarin effect through CYP inhibition and alteration "
        "of gut flora, raising INR and bleeding risk.",
        "Check INR within 3-5 days of starting or stopping ciprofloxacin.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "levothyroxine", "MODERATE",
        "Thyroid Hormone Sensitization of Warfarin",
        "Starting or increasing levothyroxine increases clotting-factor catabolism and can "
        "raise INR.",
        "Check INR 1-2 weeks after a thyroid dose change.",
        "pharmacodynamic",
    ),
    _rule(
        "warfarin", "rifampin", "MODERATE",
        "CYP Induction & Loss of Anticoagulant Effect",
        "Rifampin strongly induces CYP2C9 and CYP3A4, accelerating warfarin metabolism and "
        "reducing its anticoagulant effect.",
        "Increase warfarin per protocol with close INR monitoring; anticipate a large dose "
        "change when rifampin is started or stopped.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "warfarin", "phenytoin", "MODERATE",
        "Complex CYP-Mediated Warfarin Interaction",
        "Phenytoin can initially increase then induce warfarin metabolism, making the INR "
        "unpredictable.",
        "Monitor INR closely whenever phenytoin is started, stopped, or dose-adjusted.",
        "pharmacokinetic_cyp",
    ),
    # --- Statin / fibrate toxicity ---------------------------------------
    _rule(
        "simvastatin", "clarithromycin", "CRITICAL",
        "Potent CYP3A4 Inhibition & Acute Rhabdomyolysis Hazard",
        "Clarithromycin is a potent mechanism-based CYP3A4 inhibitor. Simvastatin exposure "
        "can rise more than 10-fold, risking rhabdomyolysis and acute kidney injury.",
        "Contraindicated. Hold simvastatin during the antibiotic course or substitute a "
        "non-CYP3A4-dependent antibiotic/statin.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "simvastatin", "itraconazole", "CRITICAL",
        "Potent CYP3A4 Inhibition & Rhabdomyolysis Hazard",
        "Itraconazole markedly inhibits CYP3A4 and can raise simvastatin exposure to "
        "dangerous levels.",
        "Contraindicated. Hold simvastatin during antifungal therapy or use a safer statin.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "simvastatin", "gemfibrozil", "CRITICAL",
        "Fibrate-Associated Myopathy & Rhabdomyolysis",
        "Gemfibrozil inhibits statin glucuronidation and OATP1B1 transport, substantially "
        "increasing simvastatin exposure and muscle toxicity.",
        "Avoid the combination. Prefer fenofibrate if a fibrate is required, with clinician "
        "review.",
        "pharmacokinetic",
    ),
    _rule(
        "atorvastatin", "clarithromycin", "MODERATE",
        "CYP3A4 Inhibition & Increased Statin Exposure",
        "Clarithromycin inhibits CYP3A4 and can raise atorvastatin exposure, increasing "
        "myopathy risk.",
        "Use the lowest effective statin dose, consider a temporary hold, and counsel on "
        "muscle pain.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "atorvastatin", "gemfibrozil", "MODERATE",
        "Fibrate-Associated Myopathy Risk",
        "Gemfibrozil can increase atorvastatin exposure and myopathy risk.",
        "Prefer fenofibrate, use the lowest statin dose, and monitor for muscle symptoms.",
        "pharmacokinetic",
    ),
    _rule(
        "amlodipine", "simvastatin", "MODERATE",
        "Amlodipine Increases Simvastatin Exposure",
        "Amlodipine inhibits CYP3A4 and can raise simvastatin levels, increasing myopathy "
        "risk.",
        "Cap simvastatin at 20 mg daily when combined with amlodipine, or use a safer statin.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "amiodarone", "simvastatin", "MODERATE",
        "Amiodarone Increases Simvastatin Exposure",
        "Amiodarone inhibits CYP3A4 and can raise simvastatin levels and myopathy risk.",
        "Cap simvastatin at 20 mg daily with amiodarone, or choose a non-CYP3A4 statin.",
        "pharmacokinetic_cyp",
    ),
    # --- Methotrexate -----------------------------------------------------
    _rule(
        "methotrexate", "aspirin", "CRITICAL",
        "Reduced Renal Clearance & Acute Methotrexate Toxicity",
        "Salicylates decrease tubular secretion of methotrexate and displace it from albumin, "
        "raising toxic serum concentrations (pancytopenia, hepatic injury).",
        "Avoid anti-inflammatory aspirin doses. Consult oncology/rheumatology before "
        "co-prescribing; monitor CBC and liver enzymes.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "methotrexate", "ibuprofen", "CRITICAL",
        "NSAID-Induced Methotrexate Accumulation",
        "NSAIDs reduce renal prostaglandin-mediated perfusion and methotrexate clearance, "
        "especially in older or dehydrated patients.",
        "Avoid NSAIDs with methotrexate, particularly at higher doses or in renal impairment. "
        "Use acetaminophen where appropriate.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "methotrexate", "naproxen", "CRITICAL",
        "NSAID-Induced Methotrexate Accumulation",
        "Naproxen can reduce methotrexate renal clearance and increase marrow toxicity.",
        "Avoid the combination; use acetaminophen and consult the prescribing specialist.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "methotrexate", "trimethoprim_sulfamethoxazole", "CRITICAL",
        "Additive Folate Antagonism & Bone Marrow Suppression",
        "Trimethoprim and methotrexate both inhibit dihydrofolate reductase, causing additive "
        "marrow toxicity.",
        "Avoid the combination. Choose a different antibiotic and monitor CBC urgently if "
        "co-exposure occurs.",
        "pharmacodynamic",
    ),
    # --- Serotonergic / CNS ------------------------------------------------
    _rule(
        "sertraline", "tramadol", "CRITICAL",
        "Synergistic Serotonergic Agonism & Serotonin Syndrome",
        "Tramadol inhibits serotonin reuptake and stimulates serotonin release, acting "
        "synergistically with SSRIs to risk serotonin syndrome.",
        "Avoid the combination. Use a non-serotonergic analgesic and counsel on agitation, "
        "tremor, fever, and clonus.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "fluoxetine", "tramadol", "CRITICAL",
        "Serotonergic Synergy & CYP2D6 Inhibition",
        "Fluoxetine inhibits CYP2D6 (reducing tramadol activation) while adding serotonergic "
        "effects, producing unpredictable analgesia and serotonin toxicity risk.",
        "Avoid the combination; choose an alternative analgesic.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "sertraline", "linezolid", "CRITICAL",
        "MAO Inhibition & Serotonin Syndrome",
        "Linezolid is a reversible non-selective MAO inhibitor; combining it with an SSRI can "
        "precipitate serotonin syndrome.",
        "Avoid unless the infection is life-threatening and the SSRI can be held with "
        "psychiatry involvement. Monitor closely.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "fluoxetine", "linezolid", "CRITICAL",
        "MAO Inhibition & Serotonin Syndrome",
        "Linezolid plus fluoxetine can cause severe serotonin toxicity.",
        "Avoid the combination; use an alternative antibiotic or hold the SSRI with "
        "specialist guidance.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "citalopram", "linezolid", "CRITICAL",
        "MAO Inhibition & Serotonin Syndrome",
        "Linezolid's MAO inhibition combined with citalopram can precipitate serotonin "
        "syndrome.",
        "Avoid the combination; seek specialist guidance.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "tramadol", "linezolid", "CRITICAL",
        "Additive Serotonergic Toxicity",
        "Both agents increase serotonergic activity; the combination can cause serotonin "
        "syndrome.",
        "Avoid; use a non-serotonergic analgesic.",
        "pharmacodynamic_neuro",
    ),
    _rule(
        "sertraline", "aspirin", "MODERATE",
        "SSRI + Antiplatelet GI Bleeding Risk",
        "SSRIs reduce platelet serotonin content and impair platelet aggregation; adding "
        "aspirin increases upper GI bleeding risk.",
        "Consider gastroprotection and monitor for black stools or bruising.",
        "pharmacodynamic",
    ),
    _rule(
        "sertraline", "ibuprofen", "MODERATE",
        "SSRI + NSAID GI Bleeding Risk",
        "SSRIs impair platelet function and NSAIDs injure the gastric mucosa, together "
        "raising GI bleeding risk.",
        "Prefer acetaminophen; if an NSAID is essential, add gastroprotection and counsel.",
        "pharmacodynamic",
    ),
    _rule(
        "fluoxetine", "aspirin", "MODERATE",
        "SSRI + Antiplatelet GI Bleeding Risk",
        "Combined serotonergic platelet depletion and antiplatelet effect increase bleeding "
        "risk.",
        "Monitor for bleeding; consider gastroprotection.",
        "pharmacodynamic",
    ),
    # --- Lithium ------------------------------------------------------------
    _rule(
        "lithium", "ibuprofen", "CRITICAL",
        "NSAID-Induced Lithium Toxicity",
        "NSAIDs reduce renal lithium clearance, raising serum levels into the toxic range "
        "(tremor, confusion, ataxia, seizures).",
        "Avoid the combination. If unavoidable, check a lithium level within 5-7 days and "
        "monitor clinically.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "lithium", "naproxen", "CRITICAL",
        "NSAID-Induced Lithium Toxicity",
        "Naproxen reduces renal lithium clearance and can precipitate toxicity.",
        "Avoid; use acetaminophen and monitor lithium levels if co-exposure occurs.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "lithium", "lisinopril", "CRITICAL",
        "ACE Inhibitor-Induced Lithium Toxicity",
        "ACE inhibitors reduce renal lithium clearance and can cause delayed lithium "
        "toxicity.",
        "Avoid or monitor lithium levels closely after starting/stopping the ACE inhibitor.",
        "pharmacokinetic_renal",
    ),
    _rule(
        "lithium", "hydrochlorothiazide", "MODERATE",
        "Thiazide-Induced Lithium Retention",
        "Thiazides increase proximal lithium reabsorption and can raise lithium levels.",
        "Check lithium levels within 5-7 days and adjust the dose.",
        "pharmacokinetic_renal",
    ),
    # --- Antiplatelet -------------------------------------------------------
    _rule(
        "clopidogrel", "omeprazole", "MODERATE",
        "CYP2C19 Inhibition & Reduced Clopidogrel Activation",
        "Omeprazole inhibits CYP2C19, reducing conversion of clopidogrel to its active "
        "metabolite and potentially lowering antiplatelet effect.",
        "Prefer pantoprazole or another PPI with less CYP2C19 inhibition when "
        "gastroprotection is needed.",
        "pharmacokinetic_cyp",
    ),
    _rule(
        "clopidogrel", "aspirin", "MODERATE",
        "Dual Antiplatelet Bleeding Risk",
        "Combined P2Y12 and COX-1 inhibition increases bleeding risk; dual therapy is "
        "sometimes intentional after stenting.",
        "Confirm the indication and duration with the prescriber; monitor for bleeding.",
        "pharmacodynamic",
    ),
    # --- Fluoroquinolone chelation -----------------------------------------
    _rule(
        "ciprofloxacin", "calcium_carbonate", "MODERATE",
        "Polyvalent Cation Chelation & Fluoroquinolone Malabsorption",
        "Calcium binds ciprofloxacin in the gut, forming insoluble chelates that can reduce "
        "antibiotic bioavailability by up to 80%.",
        "Separate doses: give ciprofloxacin at least 2 hours before or 6 hours after calcium.",
        "chelation_absorption", spacing=True, hours=3,
    ),
    _rule(
        "ciprofloxacin", "ferrous_sulfate", "MODERATE",
        "Iron Chelation & Fluoroquinolone Malabsorption",
        "Ferrous iron binds ciprofloxacin in the gut and reduces absorption.",
        "Separate doses by at least 3 hours; give ciprofloxacin first when possible.",
        "chelation_absorption", spacing=True, hours=3,
    ),
    _rule(
        "levofloxacin", "calcium_carbonate", "MODERATE",
        "Polyvalent Cation Chelation & Fluoroquinolone Malabsorption",
        "Calcium binds levofloxacin in the gut and reduces antibiotic absorption.",
        "Separate doses by at least 2-3 hours.",
        "chelation_absorption", spacing=True, hours=3,
    ),
    _rule(
        "levofloxacin", "ferrous_sulfate", "MODERATE",
        "Iron Chelation & Fluoroquinolone Malabsorption",
        "Ferrous iron binds levofloxacin and reduces absorption.",
        "Separate doses by at least 3 hours.",
        "chelation_absorption", spacing=True, hours=3,
    ),
    _rule(
        "ciprofloxacin", "tizanidine", "CRITICAL",
        "CYP1A2 Inhibition & Severe Tizanidine Toxicity",
        "Ciprofloxacin potently inhibits CYP1A2, the main enzyme clearing tizanidine, "
        "causing profound hypotension and sedation.",
        "Contraindicated. Do not co-administer; choose a different antibiotic or muscle "
        "relaxant.",
        "pharmacokinetic_cyp",
    ),
    # --- Thyroid / mineral absorption --------------------------------------
    _rule(
        "levothyroxine", "calcium_carbonate", "MODERATE",
        "Calcium Chelation & Reduced Levothyroxine Absorption",
        "Calcium binds levothyroxine in the gut and can cause clinically significant "
        "hypothyroidism.",
        "Separate by at least 4 hours. Take levothyroxine fasting in the morning and calcium "
        "with a later meal.",
        "chelation_absorption", spacing=True, hours=4,
    ),
    _rule(
        "levothyroxine", "ferrous_sulfate", "MODERATE",
        "Iron Chelation & Reduced Levothyroxine Absorption",
        "Ferrous iron binds levothyroxine in the gut, reducing thyroid hormone absorption.",
        "Separate by at least 4 hours. Take levothyroxine fasting and iron later in the day.",
        "chelation_absorption", spacing=True, hours=4,
    ),
    _rule(
        "levothyroxine", "omeprazole", "MODERATE",
        "Gastric Acid Suppression & Reduced Levothyroxine Absorption",
        "Proton pump inhibitors raise gastric pH and can reduce levothyroxine absorption, "
        "especially with dose changes.",
        "Keep the PPI schedule consistent and recheck TSH 6-8 weeks after starting or "
        "stopping it.",
        "absorption",
    ),
    _rule(
        "levothyroxine", "pantoprazole", "MODERATE",
        "Gastric Acid Suppression & Reduced Levothyroxine Absorption",
        "Pantoprazole can reduce levothyroxine absorption by raising gastric pH.",
        "Keep the PPI schedule consistent and monitor TSH after changes.",
        "absorption",
    ),
    # --- Potassium / renal ------------------------------------------------
    _rule(
        "lisinopril", "spironolactone", "MODERATE",
        "Additive Potassium Retention & Hyperkalemia Risk",
        "ACE inhibition and aldosterone antagonism both reduce renal potassium excretion, "
        "risking hyperkalemia and arrhythmia.",
        "Check potassium and creatinine within 1-2 weeks of initiation and after dose "
        "changes; avoid potassium supplements and salt substitutes.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "lisinopril", "potassium_chloride", "CRITICAL",
        "Additive Hyperkalemia & Cardiac Arrhythmia Risk",
        "ACE inhibitors reduce potassium excretion; supplemental potassium can push serum "
        "levels into a dangerous range.",
        "Do not use routinely. Check potassium and renal function; use only with documented "
        "hypokalemia and close monitoring.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "spironolactone", "potassium_chloride", "CRITICAL",
        "Additive Hyperkalemia & Cardiac Arrhythmia Risk",
        "Spironolactone retains potassium; supplementation can cause severe hyperkalemia.",
        "Avoid unless potassium is documented low and monitored closely.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "losartan", "potassium_chloride", "CRITICAL",
        "Additive Hyperkalemia & Cardiac Arrhythmia Risk",
        "ARBs reduce renal potassium excretion, and supplements can cause dangerous "
        "hyperkalemia.",
        "Avoid routine supplementation; monitor potassium and renal function.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "lisinopril", "losartan", "MODERATE",
        "Dual Renin-Angiotensin Blockade",
        "Combining an ACE inhibitor and an ARB increases hypotension, hyperkalemia, and "
        "acute kidney injury risk without added benefit for most patients.",
        "Avoid dual blockade unless a specialist has documented a specific indication; "
        "monitor potassium and creatinine.",
        "pharmacodynamic",
    ),
    _rule(
        "lisinopril", "ibuprofen", "MODERATE",
        "NSAID + ACE Inhibitor & Acute Kidney Injury Risk",
        "NSAIDs reduce renal perfusion, and ACE inhibition impairs compensatory efferent "
        "arteriolar constriction, especially during dehydration.",
        "Use the lowest NSAID dose for the shortest time; monitor renal function and blood "
        "pressure.",
        "pharmacodynamic_renal",
    ),
    _rule(
        "losartan", "ibuprofen", "MODERATE",
        "NSAID + ARB & Acute Kidney Injury Risk",
        "NSAIDs can reduce renal perfusion and worsen kidney function when combined with an "
        "ARB.",
        "Minimize NSAID use and monitor renal function.",
        "pharmacodynamic_renal",
    ),
    _rule(
        "furosemide", "lisinopril", "MODERATE",
        "Additive Hypotension & Renal Risk",
        "Diuretic-induced volume depletion plus ACE inhibition can cause first-dose "
        "hypotension and kidney injury.",
        "Monitor blood pressure and creatinine, especially after initiation or dose changes.",
        "pharmacodynamic_renal",
    ),
    _rule(
        "trimethoprim_sulfamethoxazole", "lisinopril", "MODERATE",
        "Trimethoprim-Induced Hyperkalemia With ACE Inhibition",
        "Trimethoprim blocks distal tubular potassium secretion, and ACE inhibition further "
        "reduces excretion.",
        "Check potassium within 1 week, especially in older adults or renal impairment.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "trimethoprim_sulfamethoxazole", "spironolactone", "MODERATE",
        "Additive Hyperkalemia Risk",
        "Both agents reduce renal potassium excretion.",
        "Monitor potassium closely during antibiotic therapy.",
        "pharmacodynamic_lab",
    ),
    # --- Cardiac rhythm / rate --------------------------------------------
    _rule(
        "metoprolol", "verapamil", "CRITICAL",
        "Additive Bradycardia & AV Block",
        "Both agents slow AV nodal conduction and myocardial contractility; combination can "
        "cause severe bradycardia, heart block, or hypotension.",
        "Avoid unless a cardiologist is monitoring; check heart rate, blood pressure, and ECG.",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "digoxin", "amiodarone", "CRITICAL",
        "Amiodarone-Induced Digoxin Toxicity",
        "Amiodarone inhibits P-glycoprotein and reduces digoxin clearance, raising digoxin "
        "levels and causing arrhythmia, nausea, and visual changes.",
        "Reduce the digoxin dose by approximately 50% when starting amiodarone and monitor "
        "levels.",
        "pharmacokinetic",
    ),
    _rule(
        "digoxin", "verapamil", "MODERATE",
        "Verapamil Increases Digoxin Levels & Bradycardia Risk",
        "Verapamil inhibits P-glycoprotein and adds AV nodal slowing, raising digoxin levels "
        "and bradycardia risk.",
        "Monitor digoxin level, heart rate, and ECG; consider a dose reduction.",
        "pharmacokinetic",
    ),
    _rule(
        "metoprolol", "digoxin", "MODERATE",
        "Additive Bradycardia",
        "Both agents slow AV conduction and can cause symptomatic bradycardia.",
        "Monitor heart rate and symptoms; adjust doses as needed.",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "furosemide", "digoxin", "MODERATE",
        "Diuretic-Induced Hypokalemia & Digoxin Toxicity",
        "Loop-diuretic hypokalemia increases myocardial sensitivity to digoxin and the risk "
        "of arrhythmia.",
        "Monitor potassium and magnesium; replace electrolytes as needed.",
        "pharmacodynamic_lab",
    ),
    _rule(
        "hydrochlorothiazide", "digoxin", "MODERATE",
        "Thiazide-Induced Hypokalemia & Digoxin Toxicity",
        "Thiazide-induced potassium loss can potentiate digoxin toxicity.",
        "Monitor potassium and magnesium regularly.",
        "pharmacodynamic_lab",
    ),
    # --- QT prolongation ----------------------------------------------------
    _rule(
        "azithromycin", "ondansetron", "MODERATE",
        "Additive QT Prolongation",
        "Both drugs can prolong the QT interval, increasing the risk of torsades de pointes.",
        "Check baseline ECG and electrolytes in high-risk patients; avoid other QT-prolonging "
        "drugs.",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "citalopram", "ondansetron", "MODERATE",
        "Additive QT Prolongation",
        "Citalopram and ondansetron both prolong QT; the combination raises torsades risk.",
        "Consider a different antiemetic; monitor ECG and electrolytes if co-used.",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "amiodarone", "ondansetron", "MODERATE",
        "Additive QT Prolongation",
        "Amiodarone and ondansetron can additively prolong the QT interval.",
        "Use the lowest effective ondansetron dose and monitor ECG/electrolytes.",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "ciprofloxacin", "ondansetron", "MODERATE",
        "Additive QT Prolongation",
        "Fluoroquinolones and ondansetron can both prolong QT.",
        "Assess electrolytes and ECG risk factors before combining.",
        "pharmacodynamic_cardiac",
    ),
    # --- Diabetes -----------------------------------------------------------
    _rule(
        "glipizide", "insulin", "CRITICAL",
        "Additive Hypoglycemia",
        "A sulfonylurea plus insulin can cause severe, prolonged hypoglycemia.",
        "Use with a clear insulin/sulfonylurea titration plan and frequent glucose "
        "monitoring; educate on hypoglycemia symptoms.",
        "pharmacodynamic_endocrine",
    ),
    _rule(
        "metformin", "iodinated_contrast", "MODERATE",
        "Contrast-Associated Acute Kidney Injury & Metformin Accumulation",
        "Iodinated contrast can impair renal function, reducing metformin clearance and "
        "increasing lactic acidosis risk.",
        "Hold metformin at the time of contrast and for 48 hours afterward; recheck renal "
        "function before restarting.",
        "pharmacokinetic_renal",
    ),
    # --- Enzyme / transporter interactions ---------------------------------
    _rule(
        "allopurinol", "azathioprine", "CRITICAL",
        "Xanthine Oxidase Inhibition & Severe Azathioprine Toxicity",
        "Allopurinol blocks xanthine oxidase, the main route of azathioprine inactivation, "
        "causing profound bone-marrow suppression.",
        "Avoid the combination. If unavoidable, reduce azathioprine substantially and monitor "
        "CBC closely under specialist guidance.",
        "pharmacokinetic",
    ),
    _rule(
        "sildenafil", "nitroglycerin", "CRITICAL",
        "Profound Hypotension From PDE5 + Nitrate Combination",
        "PDE5 inhibition amplifies nitrate-mediated vasodilation, causing life-threatening "
        "hypotension and myocardial ischemia.",
        "Absolutely contraindicated. Do not give nitrates within 24 hours of sildenafil (48 "
        "hours for longer-acting PDE5 inhibitors).",
        "pharmacodynamic_cardiac",
    ),
    _rule(
        "rifampin", "simvastatin", "MODERATE",
        "CYP Induction & Reduced Statin Exposure",
        "Rifampin induces CYP3A4 and can markedly reduce simvastatin exposure, lowering "
        "efficacy.",
        "Monitor lipids; consider a statin less dependent on CYP3A4.",
        "pharmacokinetic_cyp",
    ),
]


# Classes that should not be duplicated without a clear indication.
DUPLICATE_CLASS_RULES: List[Dict[str, Any]] = [
    {
        "keys": ("ibuprofen", "naproxen"),
        "severity": "MODERATE",
        "title": "Therapeutic Duplication: Two NSAIDs",
        "mechanism": "Taking two NSAIDs together adds GI, renal, and cardiovascular toxicity "
        "without providing extra benefit.",
        "clinical_action": "Use only one NSAID. Review the regimen with the prescriber or pharmacist.",
        "category": "therapeutic_duplication",
        "spacing_resolvable": False,
        "recommended_spacing_hours": 0,
    },
    {
        "keys": ("sertraline", "fluoxetine", "citalopram"),
        "severity": "CRITICAL",
        "title": "Therapeutic Duplication: Multiple SSRIs",
        "mechanism": "Combining SSRIs increases serotonin toxicity and bleeding risk without "
        "added antidepressant benefit.",
        "clinical_action": "Do not combine SSRIs. Confirm the intended regimen with the prescriber.",
        "category": "therapeutic_duplication",
        "spacing_resolvable": False,
        "recommended_spacing_hours": 0,
    },
    {
        "keys": ("simvastatin", "atorvastatin"),
        "severity": "MODERATE",
        "title": "Therapeutic Duplication: Two Statins",
        "mechanism": "Two statins add myopathy and hepatic risk without extra lipid benefit.",
        "clinical_action": "Use a single statin at the appropriate intensity.",
        "category": "therapeutic_duplication",
        "spacing_resolvable": False,
        "recommended_spacing_hours": 0,
    },
    {
        "keys": ("lisinopril", "losartan"),
        "severity": "MODERATE",
        "title": "Therapeutic Duplication: ACE Inhibitor + ARB",
        "mechanism": "Dual renin-angiotensin blockade increases hyperkalemia, hypotension, and "
        "acute kidney injury risk.",
        "clinical_action": "Avoid dual blockade unless a specialist has documented a specific indication.",
        "category": "therapeutic_duplication",
        "spacing_resolvable": False,
        "recommended_spacing_hours": 0,
    },
]


KNOWLEDGE_BASE_META = {
    "version": KNOWLEDGE_BASE_VERSION,
    "last_updated": KNOWLEDGE_BASE_UPDATED,
    "drug_count": len(DRUG_REGISTRY),
    "rule_count": len(INTERACTION_RULES) + len(DUPLICATE_CLASS_RULES),
    "sources": [
        "FDA-approved prescribing information (drug labels)",
        "NLM RxNorm naming conventions for generic and brand names",
        "Standard clinical pharmacology references for CYP450, renal clearance, "
        "pharmacodynamic synergy, and GI chelation",
    ],
    "disclaimer": DISCLAIMER,
}
