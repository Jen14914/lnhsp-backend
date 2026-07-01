"""
Seed the database with realistic data matching the LNHSP HTML template content
(districts, diseases, alerts, reports, publications, resources, dashboard series).

Run with:  python -m app.seed.seed_data
"""
from datetime import date

from app.database import Base, engine, SessionLocal
from app.models.district import District
from app.models.disease import Disease
from app.models.alert import Alert
from app.models.report import Report, DistrictCaseCount, DiseaseWeeklyCount
from app.models.publication import Publication, PublicationDiseaseTag
from app.models.resource import Resource
from app.models.dashboard import ReportingCompleteness

DISTRICTS = [
    ("maseru", "Maseru"),
    ("leribe", "Leribe"),
    ("berea", "Berea"),
    ("mafeteng", "Mafeteng"),
    ("mohales-hoek", "Mohale's Hoek"),
    ("quthing", "Quthing"),
    ("qacha", "Qacha's Nek"),
    ("mokhotlong", "Mokhotlong"),
    ("thaba-tseka", "Thaba-Tseka"),
    ("butha-buthe", "Butha-Buthe"),
]

# (slug, name, sesotho, letter, category, status, idsr, transmission, cases, trend, trend_pct,
#  desc, symptoms[list], prevention, when_to_seek, alert_note)
DISEASES = [
    ("acute-diarrhoea", "Acute Diarrhoeal Disease", "Bolwetse ba mala", "A", "idsr1", "routine",
     "IDSR Priority 1", "Faecal-oral", 154, "down", 8.0,
     "Diarrhoeal illness caused by bacterial, viral or parasitic pathogens through contaminated food or water.",
     ["Watery or bloody diarrhoea", "Abdominal cramps", "Nausea and vomiting", "Dehydration", "Fever"],
     "Boil drinking water, practise good hand hygiene, safe food handling.",
     "Seek care immediately if diarrhoea is bloody, or if signs of dehydration appear.", None),

    ("anthrax", "Anthrax", "Khohola ea mobu", "A", "zoonotic", "nocases",
     "IDSR Priority 1", "Contact / Inhalation", 0, "flat", None,
     "Serious bacterial infection caused by Bacillus anthracis, primarily affecting livestock and people in contact with infected animals.",
     ["Skin lesions with black centre", "Fever and chills", "Chest pain (inhalation form)", "Nausea and vomiting"],
     "Avoid contact with dead livestock. Vaccinate animals. Do not handle carcasses without PPE.",
     "Seek care immediately if you have handled dead animals and develop skin sores or fever.", None),

    ("cholera", "Cholera", "Lefu la maoto", "C", "idsr1", "active",
     "IDSR Priority 1", "Faecal-oral / Water", 14, "up", 40.0,
     "Acute diarrhoeal disease caused by Vibrio cholerae. Rapidly fatal without treatment due to severe dehydration.",
     ["Profuse watery diarrhoea (rice-water stools)", "Severe vomiting", "Rapid dehydration", "Muscle cramps", "Shock"],
     "Boil all drinking water. Wash hands with soap. Avoid raw foods. Use latrines.",
     "Cholera is a medical emergency. Seek care IMMEDIATELY at onset of profuse watery diarrhoea.",
     "Active outbreak in Leribe district. 14 confirmed cases, 2 deaths. Week 24, 2025."),

    ("covid19", "COVID-19", "Lefu la COVID-19", "C", "idsr2", "routine",
     "IDSR Priority 2", "Airborne / Droplet", 17, "flat", None,
     "Respiratory illness caused by SARS-CoV-2. Ranges from mild illness to severe pneumonia and death in high-risk groups.",
     ["Fever", "Dry cough", "Fatigue", "Loss of taste or smell", "Shortness of breath"],
     "Vaccination, good ventilation, hand hygiene, stay home when sick.",
     "Seek care if you have difficulty breathing, persistent chest pain, or confusion.", None),

    ("dysentery", "Dysentery (Bacillary)", "Lefu la mala a noa mali", "D", "idsr1", "routine",
     "IDSR Priority 1", "Faecal-oral", 22, "down", 5.0,
     "Intestinal infection causing bloody diarrhoea, caused by Shigella bacteria or Entamoeba histolytica.",
     ["Bloody diarrhoea", "Severe abdominal cramps", "Fever", "Painful bowel movements", "Nausea"],
     "Hand hygiene, safe water, proper sanitation.",
     "Seek care for bloody diarrhoea, especially in young children.", None),

    ("hiv", "HIV / AIDS", "Bolwetse ba HIV", "H", "sti", "routine",
     "IDSR Priority 1", "Sexual / Blood / Mother-to-child", 34, "flat", None,
     "HIV weakens the immune system. Lesotho has one of the highest HIV prevalence rates globally at approximately 23%.",
     ["Initial flu-like illness", "Weight loss", "Persistent fever", "Night sweats", "Recurrent infections"],
     "Condom use, HIV testing, PrEP, treatment as prevention, PMTCT.",
     "Get tested regularly. Start treatment immediately upon diagnosis.", None),

    ("influenza", "Influenza (Seasonal)", "Moqhoqho o moholo", "I", "idsr2", "routine",
     "IDSR Priority 2", "Airborne / Droplet", 41, "up", 10.0,
     "Acute respiratory illness caused by Influenza A or B viruses. Peaks in Lesotho's winter months (June-August).",
     ["Sudden high fever", "Severe headache", "Muscle and joint pain", "Dry cough", "Fatigue"],
     "Annual vaccination, hand hygiene, cover coughs and sneezes.",
     "Seek care if breathing becomes difficult or symptoms worsen after initial improvement.", None),

    ("malaria", "Malaria", "Lefu la mmala", "M", "idsr1", "watch",
     "IDSR Priority 1", "Mosquito bite (Anopheles)", 47, "up", 24.0,
     "Parasitic disease transmitted by Anopheles mosquitoes. Plasmodium falciparum is the predominant species in Lesotho.",
     ["Cyclical fever and chills", "Severe headache", "Muscle pain", "Nausea and vomiting", "Jaundice"],
     "Insecticide-treated bed nets, indoor residual spraying, prompt treatment.",
     "Seek care within 24 hours of fever onset if you live in or have visited a malaria area.",
     "Cases above C1 alert threshold in Quthing district. Week 24: 47 cases, 24% increase on last week."),

    ("measles", "Measles", "Mofetse", "M", "vpd", "nocases",
     "IDSR Priority 1", "Airborne / Droplet", 0, "flat", None,
     "Highly contagious viral disease. Vaccine-preventable. National vaccination campaign achieved 94% coverage in 2025.",
     ["High fever", "Cough, runny nose, red eyes", "Koplik's spots (mouth)", "Red blotchy rash starting on face"],
     "Two doses of measles vaccine (MCV1 at 9 months, MCV2 at 15 months).",
     "Seek care immediately for any child with fever and rash.", None),

    ("meningitis", "Meningitis (Bacterial)", "Lefu la boko", "M", "idsr1", "routine",
     "IDSR Priority 1", "Droplet / Direct contact", 2, "down", 50.0,
     "Life-threatening inflammation of membranes surrounding the brain and spinal cord. Caused by Neisseria meningitidis and others.",
     ["Severe sudden headache", "Stiff neck", "High fever", "Sensitivity to light", "Rash that does not fade"],
     "Vaccination (MenA, MenACWY), avoid crowded enclosed spaces during outbreaks.",
     "Seek emergency care IMMEDIATELY. Meningitis can be fatal within hours.", None),

    ("mpox", "Mpox (Monkeypox)", "Mpox", "M", "idsr2", "nocases",
     "IDSR Priority 2", "Contact / Droplet", 0, "flat", None,
     "Viral disease causing fever and characteristic skin lesions. Declared a Public Health Emergency of International Concern in 2024.",
     ["Fever and headache", "Swollen lymph nodes", "Characteristic skin rash", "Lesions on face, hands, genitals"],
     "Avoid close contact with suspected cases. Vaccination for high-risk groups.",
     "Seek care if you develop unexplained skin rash with fever, especially after contact with a case.", None),

    ("plague", "Plague", "Lefu la linonyana", "P", "idsr1", "nocases",
     "IDSR Priority 1", "Flea bite / Droplet (pneumonic)", 0, "flat", None,
     "Bacterial infection caused by Yersinia pestis. Classified as a Priority 1 disease due to epidemic potential.",
     ["Sudden high fever", "Painful swollen lymph nodes (buboes)", "Cough with bloody sputum (pneumonic)"],
     "Rodent control, avoid contact with dead rodents, flea control.",
     "Seek emergency care immediately for sudden fever with swollen painful lymph nodes.", None),

    ("rabies", "Rabies", "Bolwetse ba lintja", "R", "zoonotic", "routine",
     "IDSR Priority 1", "Animal bite / Scratch", 1, "flat", None,
     "Fatal viral encephalitis transmitted through the bite or scratch of an infected animal. Almost always fatal once symptoms appear.",
     ["Fever and headache at bite site", "Anxiety and confusion", "Hydrophobia (fear of water)", "Paralysis", "Coma"],
     "Vaccinate dogs and cats. Seek post-exposure prophylaxis (PEP) IMMEDIATELY after any animal bite.",
     "Go to a health facility IMMEDIATELY after any dog, cat, or wild animal bite -- before symptoms develop.", None),

    ("sti", "STIs (Sexually Transmitted Infections)", "Lifu tse fetisanang ka thobalano", "S", "sti", "routine",
     "IDSR Priority 2", "Sexual contact", 89, "flat", None,
     "Group of infections including gonorrhoea, syphilis, chlamydia and others. Often co-occurring with HIV.",
     ["Genital discharge or sores", "Painful urination", "Lower abdominal pain", "Rash on palms or soles (syphilis)"],
     "Condom use, regular testing, treatment of partners.",
     "Seek care promptly for any genital sores, discharge, or pain during urination.", None),

    ("tb", "Tuberculosis (TB)", "Mafu a matshoafo", "T", "idsr1", "routine",
     "IDSR Priority 1", "Airborne", 89, "down", 5.0,
     "Bacterial infection primarily affecting the lungs. Lesotho has one of the highest TB incidence rates globally, compounded by high HIV co-infection.",
     ["Persistent cough lasting 2+ weeks", "Coughing blood or mucus", "Night sweats", "Weight loss", "Fever"],
     "BCG vaccination at birth, good ventilation, HIV treatment (reduces TB risk), complete TB treatment.",
     "Seek care for any cough lasting more than 2 weeks. Get tested if you have been in contact with a TB patient.", None),

    ("typhoid", "Typhoid Fever", "Moqhoqho wa thoko", "T", "idsr1", "watch",
     "IDSR Priority 1", "Faecal-oral / Contaminated food and water", 8, "up", None,
     "Systemic bacterial infection caused by Salmonella Typhi. Transmitted through contaminated food and water.",
     ["Sustained high fever", "Headache", "Abdominal pain", "Constipation or diarrhoea", "Rose-coloured spots on trunk"],
     "Safe water, good sanitation, typhoid vaccination for high-risk groups.",
     "Seek care for persistent fever lasting more than 3 days, especially with abdominal pain.",
     "8 suspected cases under investigation in Maseru urban area. Possible shared food source. Week 23, 2025."),

    ("vhf", "Viral Haemorrhagic Fevers (VHF)", "Mafu a mafetse a madi", "V", "idsr1", "nocases",
     "IDSR Priority 1", "Contact / Vector-borne", 0, "flat", None,
     "Group of severe febrile illnesses including Ebola, Marburg, Lassa fever and Rift Valley fever. High fatality if untreated.",
     ["Sudden fever", "Severe headache and muscle pain", "Vomiting and diarrhoea", "Unexplained bleeding"],
     "Avoid contact with blood/body fluids of sick persons or animals. PPE for healthcare workers.",
     "IMMEDIATELY report any suspected VHF case to the district health office.", None),

    ("whooping-cough", "Whooping Cough (Pertussis)", "Mokhokheli", "W", "vpd", "routine",
     "IDSR Priority 2", "Airborne / Droplet", 5, "flat", None,
     "Highly contagious bacterial respiratory illness. Dangerous in unvaccinated infants.",
     ["Severe coughing fits", "Characteristic whoop sound", "Vomiting after coughing", "Exhaustion"],
     "DTP vaccination series from 6 weeks of age.",
     "Seek care for any infant with severe coughing fits or breathing difficulties.", None),

    ("yellow-fever", "Yellow Fever", "Feberu e tsoeu", "Y", "idsr1", "nocases",
     "IDSR Priority 1", "Mosquito bite (Aedes)", 0, "flat", None,
     "Viral haemorrhagic fever transmitted by Aedes mosquitoes. Required vaccination for travellers to endemic areas.",
     ["Fever, headache, muscle pain", "Jaundice (yellow skin and eyes)", "Bleeding from mouth, nose, eyes", "Kidney failure"],
     "Yellow fever vaccination (single dose, lifelong protection).",
     "Seek emergency care for jaundice with fever. Report suspected cases immediately.", None),
]

ALERTS = [
    ("cholera-leribe-2025-w24", "Cholera outbreak confirmed -- Leribe district",
     "14 confirmed cases and 2 deaths reported. Probable source: contaminated water supply in Hlotse area. "
     "Community awareness and water treatment ongoing.",
     "red", "outbreak", date(2025, 6, 13), 24, 2025, "cholera", "leribe", True, True),

    ("malaria-quthing-2025-w24", "Malaria cases above seasonal threshold -- Quthing",
     "47 cases reported week-to-date, exceeding the C1 alert threshold of 38. Indoor residual spraying activated "
     "in high-burden areas.",
     "amber", "watch", date(2025, 6, 12), 24, 2025, "malaria", "quthing", True, True),

    ("typhoid-maseru-2025-w23", "Typhoid cluster under investigation -- Maseru urban",
     "8 suspected cases with epidemiological links to a shared food source. Lab confirmation pending. Public "
     "advised to practise food safety hygiene.",
     "amber", "investigation", date(2025, 6, 9), 23, 2025, "typhoid", "maseru", True, True),

    ("measles-vaccination-2025-w22", "Measles vaccination campaign -- 94% national coverage achieved",
     "Campaign targeting children 6 months to 15 years concluded successfully. No new measles cases reported "
     "since Week 19.",
     "green", "resolved", date(2025, 6, 2), 22, 2025, "measles", None, True, True),
]

# Weekly reports (national)
WEEKLY_REPORTS = [
    ("weekly-epid-2025-w24", "National Weekly Epid. Report -- Week 24, 2025", date(2025, 6, 13), 24, 2025, 1.4),
    ("weekly-epid-2025-w23", "National Weekly Epid. Report -- Week 23, 2025", date(2025, 6, 6), 23, 2025, 1.2),
    ("weekly-epid-2025-w22", "National Weekly Epid. Report -- Week 22, 2025", date(2025, 5, 30), 22, 2025, 1.1),
    ("weekly-epid-2025-w21", "National Weekly Epid. Report -- Week 21, 2025", date(2025, 5, 23), 21, 2025, 1.3),
]

# District summaries (Week 24)
DISTRICT_REPORTS = [
    ("dist-leribe-w24", "Leribe District -- Weekly Summary Week 24, 2025", "leribe", date(2025, 6, 13), 24, 2025, 0.6),
    ("dist-maseru-w24", "Maseru District -- Weekly Summary Week 24, 2025", "maseru", date(2025, 6, 13), 24, 2025, 0.7),
    ("dist-quthing-w24", "Quthing District -- Weekly Summary Week 24, 2025", "quthing", date(2025, 6, 13), 24, 2025, 0.5),
]

# SitReps
SITREPS = [
    ("sitrep-cholera-data", "Cholera Outbreak SitRep #3 -- Leribe District", "leribe", "cholera",
     date(2025, 6, 13), 3, True, 0.4),
    ("sitrep-malaria-data", "Malaria Elevated Activity SitRep #1 -- Quthing District", "quthing", "malaria",
     date(2025, 6, 12), 1, True, 0.3),
]

# Lab + data quality reports
OTHER_REPORTS = [
    ("lab-may25", "lab", "National Health Laboratory -- Monthly Surveillance Report, May 2025",
     date(2025, 6, 5), None, 2025, 1.8),
    ("dq-w24", "dq", "Reporting Completeness & Timeliness -- Week 24, 2025 -- All 10 Districts",
     date(2025, 6, 13), 24, 2025, 0.5),
]

# Week 24 district case counts (used for the weekly report preview)
DISTRICT_W24_COUNTS = [
    ("leribe", 84), ("maseru", 66), ("quthing", 51), ("berea", 33), ("mafeteng", 26),
    ("mohales-hoek", 19), ("butha-buthe", 14), ("mokhotlong", 11), ("thaba-tseka", 9), ("qacha", 8),
]

# Top diseases this week (report preview panel)
W24_TOP_DISEASES = [
    ("cholera", 14, "up", 40.0),
    ("malaria", 47, "up", 24.0),
    ("tb", 89, "down", 5.0),
    ("typhoid", 8, "flat", None),
    ("acute-diarrhoea", 154, "down", 8.0),
]

# 12-week epi curve totals (Wk13-Wk24), national
EPI_CURVE_TOTAL = [198, 210, 225, 241, 230, 248, 260, 274, 261, 278, 264, 312]

# 12-week cholera + malaria trend (for dashboard charts)
CHOLERA_TREND = [0, 0, 1, 0, 2, 1, 0, 2, 3, 5, 10, 14]
MALARIA_TREND = [22, 28, 25, 30, 27, 31, 33, 35, 38, 42, 38, 47]
EPI_WEEKS = list(range(13, 25))  # 13..24

# National epi-curve totals the front-end expects to see (Wk13..Wk24).
# The remainder (after cholera+malaria) is spread across the other routine
# diseases so the weekly sum matches this target exactly.
EPI_CURVE_TOTAL = [198, 210, 225, 241, 230, 248, 260, 274, 261, 278, 264, 312]
_ROUTINE_FOR_FILL = ["tb", "acute-diarrhoea", "hiv", "influenza", "covid19", "sti"]

PUBLICATIONS = [
    ("monthly-bulletin-may-2025", "Monthly Epidemiological Bulletin -- May 2025", "bulletin",
     date(2025, 6, 1), 2025, "/publications/monthly-bulletin-may-2025.pdf", 3.1, True, []),
    ("cholera-outbreak-leribe-2025", "Cholera Outbreak Investigation Report -- Leribe District, 2025", "outbreak",
     date(2025, 6, 10), 2025, "/publications/cholera-outbreak-leribe-2025.pdf", 1.8, True, ["cholera"]),
    ("idsr-guidelines-v3-2025", "IDSR Case Definitions & Investigation Protocols -- Version 3, 2025", "guideline",
     date(2025, 5, 15), 2025, "/publications/idsr-guidelines-v3-2025.pdf", 4.2, True, []),
    ("monthly-bulletin-april-2025", "Monthly Epidemiological Bulletin -- April 2025", "bulletin",
     date(2025, 5, 1), 2025, "/publications/monthly-bulletin-april-2025.pdf", 2.8, False, []),
    ("annual-report-2024", "Annual Disease Surveillance Report -- Lesotho 2024", "annual",
     date(2025, 2, 15), 2024, "/publications/annual-report-2024.pdf", 12.4, False, []),
    ("malaria-outbreak-quthing-q1-2025", "Malaria Outbreak Investigation Report -- Quthing District, Q1 2025", "outbreak",
     date(2025, 4, 20), 2025, "/publications/malaria-outbreak-quthing-q1-2025.pdf", 1.6, False, ["malaria"]),
    ("typhoid-advisory-2025", "Public Health Advisory -- Typhoid Fever Prevention During Rainy Season 2025", "advisory",
     date(2025, 3, 3), 2025, "/publications/typhoid-advisory-2025.pdf", 0.9, False, ["typhoid"]),
    ("ipc-guidelines-2024", "National Infection Prevention & Control Guidelines -- 2024 Edition", "guideline",
     date(2024, 12, 1), 2024, "/publications/ipc-guidelines-2024.pdf", 5.7, False, []),
    ("mdr-tb-research-2024", "Epidemiology of Multidrug-Resistant Tuberculosis in Lesotho: A Five-Year Review (2019-2024)",
     "research", date(2024, 10, 1), 2024, "https://doi.org/example/mdr-tb-lesotho", None, False, ["tb"]),
    ("monthly-bulletin-dec-2024", "Monthly Epidemiological Bulletin -- December 2024", "bulletin",
     date(2025, 1, 2), 2024, "/publications/monthly-bulletin-dec-2024.pdf", 2.5, False, []),
    ("annual-report-2023", "Annual Disease Surveillance Report -- Lesotho 2023", "annual",
     date(2024, 2, 28), 2023, "/publications/annual-report-2023.pdf", 10.8, False, []),
    ("measles-outbreak-review-2024", "Measles Outbreak After-Action Review -- Maseru & Berea Districts, 2024", "outbreak",
     date(2024, 9, 14), 2024, "/publications/measles-outbreak-review-2024.pdf", 2.1, False, ["measles"]),
]

RESOURCES = [
    ("idsr-case-notification-form", "IDSR Case Notification Form",
     "Standard form for reporting suspected and confirmed IDSR priority disease cases from facility level to district.",
     "forms", "/resources/idsr-case-notification-form.pdf", "PDF", "Version 4.1", date(2025, 1, 1), True),
    ("district-line-listing-template", "District Line Listing Template",
     "Excel line listing template for recording individual case details during outbreak investigations. "
     "Pre-formatted with validation rules.",
     "forms", "/resources/district-line-listing-template.xlsx", "XLS", "Version 2.3", date(2025, 3, 1), True),
    ("outbreak-investigation-form", "Outbreak Investigation Form",
     "Comprehensive field form for epidemiological investigation of confirmed or suspected outbreaks. Includes "
     "case definition, exposure mapping and hypothesis sections.",
     "forms", "/resources/outbreak-investigation-form.pdf", "PDF", "Version 3.0", date(2025, 2, 1), True),
    ("contact-tracing-form", "Contact Tracing Form",
     "Used for tracking and monitoring contacts of confirmed cases of priority communicable diseases. Includes "
     "daily follow-up symptom checklist.",
     "forms", "/resources/contact-tracing-form.pdf", "PDF", "Version 2.0", date(2025, 1, 1), True),
    ("weekly-idsr-summary-form", "Weekly IDSR Summary Form",
     "Weekly aggregate reporting template for facilities to summarise IDSR disease counts before entering into "
     "DHIS2. For use where internet access is unavailable.",
     "forms", "/resources/weekly-idsr-summary-form.xlsx", "XLS", "Version 1.8", date(2024, 12, 1), True),
    ("lab-specimen-request-form", "Laboratory Specimen Request Form",
     "Specimen submission form for sending samples to the National Health Laboratory for confirmation of "
     "suspected outbreak pathogens.",
     "forms", "/resources/lab-specimen-request-form.pdf", "PDF", "Version 1.5", date(2024, 11, 1), False),
    ("sop-outbreak-detection", "SOP: Outbreak Detection & Response Activation",
     "Step-by-step procedure for district health officers to detect, verify, and activate outbreak response. "
     "Covers C1 and C2 alert thresholds.",
     "sop", "/resources/sop-outbreak-detection.pdf", "PDF", "SOP-SURV-001 · v2.1", date(2025, 2, 1), False),
    ("sop-specimen-transport", "SOP: Specimen Collection & Transport",
     "Procedures for collecting, packaging, and transporting biological specimens to the National Health "
     "Laboratory under biosafety conditions.",
     "sop", "/resources/sop-specimen-transport.pdf", "PDF", "SOP-LAB-003 · v1.4", date(2025, 1, 1), False),
    ("sop-dhis2-data-entry", "SOP: DHIS2 Weekly Data Entry",
     "Step-by-step guide for facility data clerks to enter weekly IDSR aggregate data into DHIS2 accurately and "
     "on time.",
     "sop", "/resources/sop-dhis2-data-entry.pdf", "PDF", "SOP-DATA-002 · v3.0", date(2025, 3, 1), False),
    ("national-health-policy-2023", "National Health Policy -- Lesotho 2023-2030",
     "The overarching national health policy framework guiding Lesotho's health system priorities, including "
     "communicable disease prevention and control.",
     "policy", "/resources/national-health-policy-2023.pdf", "PDF", "Official · MoH 2023", date(2023, 1, 1), False),
    ("idsr-policy-strategy-2022", "National IDSR Policy & Strategy 2022-2027",
     "Integrated Disease Surveillance and Response policy outlining Lesotho's commitments to the International "
     "Health Regulations and Africa CDC IDSR framework.",
     "policy", "/resources/idsr-policy-strategy-2022.pdf", "PDF", "Official · MoH 2022", date(2022, 7, 1), False),
    ("idsr-training-facilitator-guide", "IDSR Surveillance Officer Training -- Facilitator Guide",
     "Complete facilitator package for conducting district-level IDSR training workshops. Includes slide deck, "
     "participant manual, exercises and evaluation tools.",
     "training", "/resources/idsr-training-facilitator-guide.zip", "ZIP", "2024 Edition", date(2024, 10, 1), False),
    ("chw-job-aid", "Community Health Worker Surveillance Job Aid",
     "Laminated pocket-sized job aid for CHWs covering danger signs for priority diseases, referral criteria, "
     "and reporting steps in simple language and Sesotho.",
     "training", "/resources/chw-job-aid.pdf", "PDF", "Sesotho / English", date(2024, 6, 1), False),
    ("cholera-prevention-poster", "Cholera Prevention Poster -- Sesotho / English",
     "A3 printable awareness poster for clinic and community waiting areas. Covers boiling water, handwashing, "
     "safe food handling and when to seek care.",
     "iec", "/resources/cholera-prevention-poster.pdf", "PDF", "Print-ready A3", date(2025, 4, 1), False),
    ("malaria-prevention-flyer", "Malaria Prevention Community Flyer",
     "Printable community awareness flyer on malaria prevention -- insecticide-treated nets, indoor spraying, "
     "early treatment seeking. Available in Sesotho.",
     "iec", "/resources/malaria-prevention-flyer.pdf", "PDF", "Print-ready A5", date(2025, 1, 1), False),
]

# Reporting completeness heatmap (Week 17-24), per district
COMPLETENESS_WEEKS = list(range(17, 25))
COMPLETENESS_GRID = {
    "maseru":       ["submitted"] * 8,
    "leribe":       ["submitted", "late", "submitted", "submitted", "submitted", "submitted", "submitted", "submitted"],
    "berea":        ["submitted", "submitted", "submitted", "late", "submitted", "submitted", "submitted", "submitted"],
    "mafeteng":     ["submitted", "submitted", "missing", "late", "submitted", "submitted", "submitted", "submitted"],
    "mohales-hoek": ["late", "submitted", "submitted", "submitted", "submitted", "late", "submitted", "submitted"],
    "quthing":      ["submitted"] * 8,
    "qacha":        ["submitted", "submitted", "late", "submitted", "missing", "submitted", "submitted", "submitted"],
    "mokhotlong":   ["missing", "late", "submitted", "submitted", "submitted", "submitted", "submitted", "submitted"],
    "thaba-tseka":  ["submitted", "submitted", "submitted", "late", "submitted", "submitted", "late", "submitted"],
    "butha-buthe":  ["submitted"] * 8,
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(District).first():
            print("Database already seeded -- skipping. Delete the DB file / drop tables to reseed.")
            return

        # Districts
        district_by_slug = {}
        for slug, name in DISTRICTS:
            d = District(slug=slug, name=name)
            db.add(d)
            district_by_slug[slug] = d
        db.flush()

        # Diseases
        disease_by_slug = {}
        for (slug, name, sesotho, letter, category, status, idsr, transmission, cases, trend, trend_pct,
             desc, symptoms, prevention, when_to_seek, alert_note) in DISEASES:
            dis = Disease(
                slug=slug, name=name, sesotho_name=sesotho, letter=letter,
                category=category, status=status, idsr_priority=idsr, transmission=transmission,
                cases_this_week=cases, trend=trend, trend_pct=trend_pct,
                description=desc, symptoms="\n".join(symptoms), prevention=prevention,
                when_to_seek_care=when_to_seek, active_alert_note=alert_note,
            )
            db.add(dis)
            disease_by_slug[slug] = dis
        db.flush()

        # Alerts
        for (slug, title, body, level, tag, pub_date, week, year, disease_slug, district_slug,
             is_ticker, is_active) in ALERTS:
            db.add(Alert(
                slug=slug, title=title, body=body, level=level, tag=tag,
                published_date=pub_date, epi_week=week, epi_year=year,
                disease_id=disease_by_slug[disease_slug].id if disease_slug else None,
                district_id=district_by_slug[district_slug].id if district_slug else None,
                is_ticker=is_ticker, is_active=is_active,
            ))

        # Weekly national reports
        report_by_slug = {}
        for slug, title, pub_date, week, year, size in WEEKLY_REPORTS:
            r = Report(
                slug=slug, report_type="weekly", title=title, published_date=pub_date,
                epi_week=week, epi_year=year, district_id=None,
                file_url=f"/reports/{slug}.pdf", file_size_mb=size,
            )
            db.add(r)
            report_by_slug[slug] = r
        db.flush()

        # Attach Week 24 preview data (district + disease breakdowns) to the latest weekly report
        w24 = report_by_slug["weekly-epid-2025-w24"]
        w24.active_outbreaks = 3
        w24.total_cases = 312
        w24.deaths = 2
        w24.districts_reporting = "10/10"
        for district_slug, count in DISTRICT_W24_COUNTS:
            db.add(DistrictCaseCount(
                report_id=w24.id, district_id=district_by_slug[district_slug].id, case_count=count
            ))
        for disease_slug, count, trend, trend_pct in W24_TOP_DISEASES:
            db.add(DiseaseWeeklyCount(
                report_id=w24.id, disease_id=disease_by_slug[disease_slug].id,
                epi_year=2025, epi_week=24, case_count=count, trend=trend, trend_pct=trend_pct,
            ))

        # District summaries
        for slug, title, district_slug, pub_date, week, year, size in DISTRICT_REPORTS:
            db.add(Report(
                slug=slug, report_type="district", title=title, published_date=pub_date,
                epi_week=week, epi_year=year, district_id=district_by_slug[district_slug].id,
                file_url=f"/reports/{slug}.pdf", file_size_mb=size,
            ))

        # SitReps
        for slug, title, district_slug, disease_slug, pub_date, num, active, size in SITREPS:
            db.add(Report(
                slug=slug, report_type="sitrep", title=title,
                district_id=district_by_slug[district_slug].id,
                disease_id=disease_by_slug[disease_slug].id,
                published_date=pub_date, sitrep_number=num, is_sitrep_active=active,
                file_url=f"/reports/{slug}.pdf", file_size_mb=size,
            ))

        # Lab + DQ reports
        for slug, rtype, title, pub_date, week, year, size in OTHER_REPORTS:
            db.add(Report(
                slug=slug, report_type=rtype, title=title, published_date=pub_date,
                epi_week=week, epi_year=year, file_url=f"/reports/{slug}.pdf", file_size_mb=size,
            ))

        # 12-week epi curve + disease trend series (no report_id -- used by dashboard charts)
        for i, week in enumerate(EPI_WEEKS):
            if week == 24:
                # Week 24's national total is already fully accounted for by
                # the report-attached breakdown below (W24_TOP_DISEASES,
                # linked to the weekly-epid-2025-w24 report). Adding a
                # second, report_id=None series for week 24 here would
                # double-count it in the dashboard's epi-curve sum.
                continue
            db.add(DiseaseWeeklyCount(
                report_id=None, disease_id=disease_by_slug["cholera"].id,
                epi_year=2025, epi_week=week, case_count=CHOLERA_TREND[i],
            ))
            db.add(DiseaseWeeklyCount(
                report_id=None, disease_id=disease_by_slug["malaria"].id,
                epi_year=2025, epi_week=week, case_count=MALARIA_TREND[i],
            ))
            # Spread the remainder of the national target evenly across a
            # fixed set of routine diseases so the weekly sum (used by the
            # epi-curve chart) matches EPI_CURVE_TOTAL exactly.
            remainder = EPI_CURVE_TOTAL[i] - CHOLERA_TREND[i] - MALARIA_TREND[i]
            n = len(_ROUTINE_FOR_FILL)
            base, extra = divmod(remainder, n)
            for j, slug in enumerate(_ROUTINE_FOR_FILL):
                count = base + (1 if j < extra else 0)
                db.add(DiseaseWeeklyCount(
                    report_id=None, disease_id=disease_by_slug[slug].id,
                    epi_year=2025, epi_week=week, case_count=count,
                ))

        # Publications
        for slug, title, pub_type, pub_date, year, file_url, size, featured, tags in PUBLICATIONS:
            pub = Publication(
                slug=slug, title=title, pub_type=pub_type, published_date=pub_date, year=year,
                file_url=file_url, file_format="PDF" if not file_url.startswith("http") else "Link",
                file_size_mb=size, is_featured=featured, is_external_link=file_url.startswith("http"),
            )
            db.add(pub)
            db.flush()
            for tag in tags:
                db.add(PublicationDiseaseTag(publication_id=pub.id, disease_slug=tag))

        # Resources
        for (slug, title, desc, category, file_url, fmt, version, updated, quick) in RESOURCES:
            db.add(Resource(
                slug=slug, title=title, description=desc, category=category,
                file_url=file_url, file_format=fmt, version_label=version,
                updated_date=updated, is_quick_download=quick,
            ))

        # Reporting completeness heatmap
        for district_slug, statuses in COMPLETENESS_GRID.items():
            for week, status in zip(COMPLETENESS_WEEKS, statuses):
                db.add(ReportingCompleteness(
                    district_id=district_by_slug[district_slug].id,
                    epi_year=2025, epi_week=week, status=status,
                ))

        db.commit()
        print("Seed complete:")
        print(f"  Districts:    {len(DISTRICTS)}")
        print(f"  Diseases:     {len(DISEASES)}")
        print(f"  Alerts:       {len(ALERTS)}")
        print(f"  Reports:      {len(WEEKLY_REPORTS) + len(DISTRICT_REPORTS) + len(SITREPS) + len(OTHER_REPORTS)}")
        print(f"  Publications: {len(PUBLICATIONS)}")
        print(f"  Resources:    {len(RESOURCES)}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
