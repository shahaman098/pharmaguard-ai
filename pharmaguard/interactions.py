"""Pharmacological knowledge base and drug interaction database.

Includes curated clinical interaction rules derived from FDA FAERS,
RxNorm, and standard clinical pharmacology guidelines (CYP450 metabolism,
pharmacodynamic synergy, and gastrointestinal chelation).
"""

from typing import Dict, List, Any

# Clinical Drug Registry with therapeutic class, default timing, and food notes
DRUG_REGISTRY: Dict[str, Dict[str, Any]] = {
    "warfarin": {
        "name": "Warfarin",
        "brand": "Coumadin",
        "class": "Anticoagulant (Vitamin K Antagonist)",
        "default_dose": "5 mg",
        "default_time": "Evening",
        "cyp_pathway": "CYP2C9",
        "food_warnings": "Maintain consistent intake of Vitamin K-rich green vegetables."
    },
    "simvastatin": {
        "name": "Simvastatin",
        "brand": "Zocor",
        "class": "HMG-CoA Reductase Inhibitor (Statin)",
        "default_dose": "20 mg",
        "default_time": "Bedtime",
        "cyp_pathway": "CYP3A4 substrate",
        "food_warnings": "Avoid grapefruit and grapefruit juice."
    },
    "clarithromycin": {
        "name": "Clarithromycin",
        "brand": "Biaxin",
        "class": "Macrolide Antibiotic",
        "default_dose": "500 mg",
        "default_time": "Morning & Evening",
        "cyp_pathway": "Potent CYP3A4 inhibitor",
        "food_warnings": "May be taken with or without food."
    },
    "ciprofloxacin": {
        "name": "Ciprofloxacin",
        "brand": "Cipro",
        "class": "Fluoroquinolone Antibiotic",
        "default_dose": "500 mg",
        "default_time": "Morning & Evening",
        "cyp_pathway": "CYP1A2 inhibitor",
        "food_warnings": "Do NOT take with dairy products or calcium-fortified juice alone."
    },
    "ibuprofen": {
        "name": "Ibuprofen",
        "brand": "Advil / Motrin",
        "class": "NSAID",
        "default_dose": "400 mg",
        "default_time": "With meals",
        "cyp_pathway": "CYP2C9 inhibitor",
        "food_warnings": "Take with food or milk to prevent GI irritation."
    },
    "calcium_carbonate": {
        "name": "Calcium Carbonate",
        "brand": "Tums / Caltrate",
        "class": "Mineral Supplement / Antacid",
        "default_dose": "600 mg",
        "default_time": "Morning",
        "cyp_pathway": "None (Polyvalent Cation)",
        "food_warnings": "Take with meals for optimal absorption."
    },
    "lisinopril": {
        "name": "Lisinopril",
        "brand": "Prinivil / Zestril",
        "class": "ACE Inhibitor",
        "default_dose": "10 mg",
        "default_time": "Morning",
        "cyp_pathway": "Renal elimination",
        "food_warnings": "Avoid salt substitutes containing potassium."
    },
    "spironolactone": {
        "name": "Spironolactone",
        "brand": "Aldactone",
        "class": "Potassium-Sparing Diuretic",
        "default_dose": "25 mg",
        "default_time": "Morning",
        "cyp_pathway": "Renal / Hepatic",
        "food_warnings": "Avoid high-potassium foods and salt substitutes."
    },
    "methotrexate": {
        "name": "Methotrexate",
        "brand": "Trexall",
        "class": "Antimetabolite / Immunosuppressant",
        "default_dose": "15 mg weekly",
        "default_time": "Morning",
        "cyp_pathway": "Renal clearance",
        "food_warnings": "Take on empty stomach or as directed with folic acid supplementation."
    },
    "aspirin": {
        "name": "Aspirin",
        "brand": "Bayer",
        "class": "Antiplatelet / Salicylate",
        "default_dose": "81 mg",
        "default_time": "Morning",
        "cyp_pathway": "Renal / Hepatic",
        "food_warnings": "Take with food to minimize GI distress."
    },
    "sertraline": {
        "name": "Sertraline",
        "brand": "Zoloft",
        "class": "SSRI Antidepressant",
        "default_dose": "50 mg",
        "default_time": "Morning",
        "cyp_pathway": "CYP2D6 / CYP3A4",
        "food_warnings": "Take in morning to prevent insomnia."
    },
    "tramadol": {
        "name": "Tramadol",
        "brand": "Ultram",
        "class": "Opioid Analgesic / Serotonergic",
        "default_dose": "50 mg",
        "default_time": "As needed",
        "cyp_pathway": "CYP2D6 / CYP3A4",
        "food_warnings": "May cause dizziness; avoid alcohol."
    },
    "metformin": {
        "name": "Metformin",
        "brand": "Glucophage",
        "class": "Biguanide Antidiabetic",
        "default_dose": "500 mg",
        "default_time": "Morning & Evening",
        "cyp_pathway": "Renal tubular secretion",
        "food_warnings": "Take with meals to reduce gastrointestinal upset."
    },
    "levothyroxine": {
        "name": "Levothyroxine",
        "brand": "Synthroid",
        "class": "Thyroid Hormone (T4)",
        "default_dose": "75 mcg",
        "default_time": "Morning (fasting)",
        "cyp_pathway": "Hepatic / Renal",
        "food_warnings": "Take 30-60 minutes before breakfast with a full glass of water."
    },
    "ferrous_sulfate": {
        "name": "Ferrous Sulfate (Iron)",
        "brand": "Feosol",
        "class": "Mineral Supplement",
        "default_dose": "325 mg",
        "default_time": "Midday",
        "cyp_pathway": "None (Divalent Cation)",
        "food_warnings": "Vitamin C enhances absorption; calcium and tea inhibit absorption."
    }
}

# Landmark Pairwise Interactions Table
INTERACTION_RULES: List[Dict[str, Any]] = [
    {
        "pair": ("warfarin", "ibuprofen"),
        "severity": "CRITICAL",
        "title": "Severe Synergistic Bleeding & GI Mucosal Hemorrhage",
        "mechanism": "NSAIDs inhibit platelet aggregation (COX-1) and cause gastric mucosal erosions, while Warfarin impairs clotting factor synthesis. Dual use dramatically escalates gastrointestinal bleeding risk.",
        "clinical_action": "Avoid combination. Recommend physician substitute with Acetaminophen (max 2g/day) for mild-to-moderate analgesia, or prescribe co-protective PPI therapy.",
        "category": "pharmacodynamic",
        "spacing_resolvable": False
    },
    {
        "pair": ("simvastatin", "clarithromycin"),
        "severity": "CRITICAL",
        "title": "Potent CYP3A4 Inhibition & Acute Rhabdomyolysis Hazard",
        "mechanism": "Clarithromycin is a potent mechanism-based inhibitor of hepatic CYP3A4. Co-administration causes a >10-fold surge in Simvastatin plasma concentration, risking severe skeletal muscle breakdown (rhabdomyolysis) and acute renal failure.",
        "clinical_action": "Contraindicated. Temporarily suspend Simvastatin during the Clarithromycin antibiotic course, or substitute with an antibiotic that does not inhibit CYP3A4 (e.g. Azithromycin).",
        "category": "pharmacokinetic_cyp",
        "spacing_resolvable": False
    },
    {
        "pair": ("ciprofloxacin", "calcium_carbonate"),
        "severity": "MODERATE",
        "title": "Polyvalent Cation Chelation & Fluoroquinolone Malabsorption",
        "mechanism": "Divalent and trivalent cations (Ca2+, Mg2+, Fe2+, Al3+) bind to oral Ciprofloxacin in the gastrointestinal lumen, forming insoluble chelates that reduce antibiotic bioavailability by up to 80%, risking clinical treatment failure.",
        "clinical_action": "Temporally separate administration. Administer Ciprofloxacin at least 2 hours before or 6 hours after Calcium Carbonate.",
        "category": "chelation_absorption",
        "spacing_resolvable": True,
        "recommended_spacing_hours": 3
    },
    {
        "pair": ("lisinopril", "spironolactone"),
        "severity": "MODERATE",
        "title": "Additive Potassium Retention & Severe Hyperkalemia Risk",
        "mechanism": "Both ACE inhibitors and aldosterone antagonists decrease renal potassium excretion. Concurrent use can precipitate life-threatening cardiac arrhythmias secondary to hyperkalemia.",
        "clinical_action": "Requires routine monitoring of serum potassium and creatinine within 1–2 weeks of initiation. Advise patient against potassium-based salt substitutes.",
        "category": "pharmacodynamic_lab",
        "spacing_resolvable": False
    },
    {
        "pair": ("methotrexate", "aspirin"),
        "severity": "CRITICAL",
        "title": "Reduced Renal Clearance & Acute Methotrexate Toxicity",
        "mechanism": "Salicylates decrease tubular secretion of Methotrexate and displace it from serum albumin binding sites, leading to elevated toxic serum Methotrexate concentrations (pancytopenia, hepatic necrosis).",
        "clinical_action": "Contraindicated at anti-inflammatory doses of Aspirin. Consult oncologist or rheumatologist before co-prescribing.",
        "category": "pharmacokinetic_renal",
        "spacing_resolvable": False
    },
    {
        "pair": ("sertraline", "tramadol"),
        "severity": "CRITICAL",
        "title": "Synergistic Serotonergic Agonism & Serotonin Syndrome",
        "mechanism": "Tramadol inhibits serotonin reuptake and stimulates serotonin release, acting synergistically with SSRIs to risk life-threatening Serotonin Syndrome (hyperthermia, clonus, autonomic instability).",
        "clinical_action": "Avoid combination. Consider alternative non-serotonergic analgesics. Monitor closely for mental status changes, tremor, and tachycardia.",
        "category": "pharmacodynamic_neuro",
        "spacing_resolvable": False
    },
    {
        "pair": ("levothyroxine", "ferrous_sulfate"),
        "severity": "MODERATE",
        "title": "Intestinal Iron Chelation of Exogenous Thyroxine",
        "mechanism": "Ferrous ions bind to Levothyroxine in the gut, forming an unabsorbable complex that leads to clinically significant hypothyroidism.",
        "clinical_action": "Separate dose timing by at least 4 hours. Take Levothyroxine fasting in the morning; take Iron supplement in the afternoon.",
        "category": "chelation_absorption",
        "spacing_resolvable": True,
        "recommended_spacing_hours": 4
    },
    {
        "pair": ("aspirin", "warfarin"),
        "severity": "CRITICAL",
        "title": "Dual Antiplatelet & Anticoagulant Hemorrhagic Synergy",
        "mechanism": "Combined inhibition of platelet plug formation and coagulation cascade proteins dramatically raises major bleeding incidence.",
        "clinical_action": "Dual therapy is strictly restricted to clinical indications with cardiologist authorization (e.g. recent coronary stent).",
        "category": "pharmacodynamic",
        "spacing_resolvable": False
    }
]
