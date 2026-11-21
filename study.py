"""Study content: modules, YouTube videos and mock-test questions for each career in data.py.

VIDEOS
  Each video has a `query`. Until you add a real `id` (the 11-character part after `v=` in a
  YouTube link), the app shows an "Open on YouTube" button that runs that search. Once you paste
  a verified id, the video is embedded and plays inside the app. Example:
      v("UPSC polity basics", "UPSC polity basics for beginners", "AbCdEfGhIjK")

QUESTIONS
  q(text, [four options], index_of_correct_option, "why it is correct")
"""
from __future__ import annotations

import re

YT_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def v(title: str, query: str, vid: str | None = None) -> dict:
    return {"title": title, "query": query, "id": vid if vid and YT_ID.match(vid) else None}


def m(mid: str, title: str, summary: str, topics: list[str], videos: list[dict]) -> dict:
    return {"id": mid, "title": title, "summary": summary, "topics": topics, "videos": videos}


def q(text: str, options: list[str], answer: int, why: str) -> dict:
    return {"text": text, "options": options, "answer": answer, "why": why}


STUDY = {
    # ------------------------------------------------------------------ civil
    "ias": {
        "modules": [
            m("polity", "Indian polity & Constitution", "The base of both Prelims and Mains.",
              ["Fundamental Rights & Duties", "Parliament & State legislatures", "Judiciary", "Constitutional amendments"],
              [v("Polity full course", "UPSC polity full course Laxmikant"), v("Fundamental Rights", "UPSC fundamental rights explained")]),
            m("history", "History & culture", "Ancient, medieval, modern India and art & culture.",
              ["Freedom struggle", "Medieval India", "Art & architecture", "Post-independence India"],
              [v("Modern India overview", "UPSC modern Indian history overview"), v("Art and culture", "UPSC art and culture NCERT")]),
            m("geo-eco", "Geography & economy", "Physical geography, resources and basic economics.",
              ["Monsoon & climate", "Rivers & landforms", "Budget & fiscal policy", "Inflation & banking basics"],
              [v("Indian geography", "UPSC Indian geography complete"), v("Indian economy", "UPSC Indian economy basics")]),
            m("csat-essay", "CSAT, current affairs & essay", "Reasoning, comprehension and answer writing.",
              ["Reading comprehension", "Basic numeracy", "Daily current affairs", "Essay & answer writing"],
              [v("CSAT strategy", "UPSC CSAT preparation strategy"), v("Answer writing", "UPSC mains answer writing practice")]),
        ],
        "questions": [
            q("Who is the constitutional head of the Indian state?", ["Prime Minister", "President", "Chief Justice of India", "Speaker of Lok Sabha"], 1, "The President is the constitutional head; the Prime Minister heads the government."),
            q("Article 21 of the Constitution protects:", ["Freedom of speech", "Right to equality", "Right to life and personal liberty", "Right to property"], 2, "Article 21 guarantees life and personal liberty."),
            q("The Constitution of India came into effect on:", ["15 August 1947", "26 November 1949", "26 January 1950", "2 October 1950"], 2, "It was adopted on 26 Nov 1949 and came into effect on 26 Jan 1950."),
            q("Fundamental Duties were added by which Constitutional Amendment?", ["42nd", "44th", "52nd", "73rd"], 0, "The 42nd Amendment (1976) added Fundamental Duties."),
            q("Who is the ex-officio Chairman of the Rajya Sabha?", ["Prime Minister", "Speaker", "Vice-President", "Attorney General"], 2, "The Vice-President of India chairs the Rajya Sabha."),
        ],
    },
    "ifs": {
        "modules": [
            m("ir", "International relations", "How states, blocs and institutions interact.",
              ["India's foreign policy", "Neighbourhood relations", "Major powers", "Global groupings"],
              [v("India foreign policy", "UPSC India foreign policy basics"), v("International relations", "UPSC international relations current")]),
            m("orgs", "International organisations", "UN system, WTO, regional groups.",
              ["UN and its agencies", "WTO, IMF, World Bank", "SAARC, BRICS, QUAD", "Non-Aligned Movement"],
              [v("UN system", "United Nations system explained UPSC"), v("Regional groupings", "SAARC BRICS QUAD UPSC")]),
            m("diplomacy", "Diplomacy & treaties", "How diplomacy works in practice.",
              ["Vienna Convention", "Bilateral vs multilateral", "Soft power", "Trade agreements"],
              [v("Diplomacy basics", "diplomacy basics for IFS aspirants"), v("Vienna Convention", "Vienna Convention diplomatic relations explained")]),
            m("language", "Language & general studies", "Languages and the common UPSC base.",
              ["Foreign language skills", "Polity & history", "Current affairs", "Essay writing"],
              [v("Current affairs", "UPSC daily current affairs"), v("IFS journey", "how to become IFS officer")]),
        ],
        "questions": [
            q("The headquarters of the United Nations is in:", ["Geneva", "New York", "Paris", "Vienna"], 1, "The UN headquarters is in New York City."),
            q("Which of these was NOT a founding leader of the Non-Aligned Movement?", ["Jawaharlal Nehru", "Josip Broz Tito", "Gamal Abdel Nasser", "Winston Churchill"], 3, "Nehru, Tito and Nasser were founders; Churchill was not."),
            q("The SAARC Secretariat is located in:", ["New Delhi", "Dhaka", "Colombo", "Kathmandu"], 3, "SAARC's secretariat is in Kathmandu, Nepal."),
            q("The World Trade Organization is headquartered in:", ["Geneva", "London", "Washington D.C.", "Singapore"], 0, "The WTO is based in Geneva, Switzerland."),
            q("The Vienna Convention on Diplomatic Relations was adopted in:", ["1948", "1961", "1972", "1991"], 1, "It was adopted in 1961."),
        ],
    },
    # ---------------------------------------------------------------- defence
    "nda": {
        "modules": [
            m("maths", "Mathematics", "Half of the written paper.",
              ["Algebra & trigonometry", "Calculus basics", "Matrices", "Probability & statistics"],
              [v("NDA maths", "NDA maths preparation full course"), v("Trigonometry", "NDA trigonometry class 11 12")]),
            m("gat", "General ability: English & GK", "Language and general knowledge.",
              ["Grammar & vocabulary", "Physics & chemistry basics", "History & geography", "Current events"],
              [v("NDA English", "NDA English grammar preparation"), v("NDA GK", "NDA general knowledge preparation")]),
            m("ssb", "SSB interview", "Personality and officer-like qualities.",
              ["Psychology tests", "Group tasks", "Personal interview", "Conference"],
              [v("SSB process", "SSB interview process explained"), v("SSB tips", "SSB interview tips NDA")]),
            m("fitness", "Physical fitness", "Medical and fitness standards.",
              ["Running & endurance", "Strength basics", "Medical standards", "Daily routine"],
              [v("NDA fitness", "NDA physical fitness preparation"), v("NDA medical", "NDA medical standards explained")]),
        ],
        "questions": [
            q("A train at 60 km/h covers 150 km in:", ["2 hours", "2.5 hours", "3 hours", "3.5 hours"], 1, "Time = 150 ÷ 60 = 2.5 hours."),
            q("The National Defence Academy is located in:", ["Dehradun", "Pune (Khadakwasla)", "Hyderabad", "Chennai"], 1, "NDA is at Khadakwasla near Pune."),
            q("What is the value of sin 30°?", ["1", "√3/2", "1/2", "0"], 2, "sin 30° = 1/2."),
            q("The tendency of a body to resist change in motion is called:", ["Momentum", "Inertia", "Friction", "Impulse"], 1, "That is inertia (Newton's first law)."),
            q("Which is India's highest peacetime gallantry award?", ["Kirti Chakra", "Shaurya Chakra", "Ashoka Chakra", "Vir Chakra"], 2, "The Ashoka Chakra is the highest peacetime gallantry award."),
        ],
    },
    # ---------------------------------------------------------------- banking
    "rbi": {
        "modules": [
            m("economics", "Economic & social issues", "Core of Phase 1 and Phase 2.",
              ["Growth & development", "Inflation", "Poverty & inequality", "Budget basics"],
              [v("RBI Grade B ESI", "RBI Grade B economic and social issues"), v("Indian economy", "Indian economy for RBI Grade B")]),
            m("finance", "Finance & management", "Financial system and markets.",
              ["Banking system", "Money & capital markets", "Monetary policy", "Management basics"],
              [v("Finance & management", "RBI Grade B finance and management"), v("Monetary policy", "monetary policy repo CRR SLR explained")]),
            m("quant-reason", "Quant & reasoning", "Aptitude for Phase 1.",
              ["Percentages & interest", "Data interpretation", "Puzzles & seating", "Number series"],
              [v("Quant for RBI", "RBI Grade B quant preparation"), v("Reasoning", "RBI Grade B reasoning preparation")]),
            m("english", "English & descriptive writing", "Comprehension and writing.",
              ["Reading comprehension", "Error spotting", "Essay & precis", "Current banking news"],
              [v("RBI English", "RBI Grade B English descriptive writing"), v("Banking news", "RBI Grade B current affairs banking")]),
        ],
        "questions": [
            q("The Reserve Bank of India was established in:", ["1925", "1935", "1947", "1969"], 1, "RBI was established on 1 April 1935."),
            q("The repo rate is the rate at which:", ["Banks lend to the public", "RBI lends short-term to commercial banks", "Banks lend to each other", "Government borrows from RBI"], 1, "Repo is the rate at which RBI lends to banks against securities."),
            q("CRR refers to the portion of deposits banks must keep:", ["In government bonds", "As cash in hand", "With the RBI", "In gold"], 2, "Cash Reserve Ratio is maintained with the RBI."),
            q("India's flexible inflation targeting framework mainly tracks which index?", ["WPI", "CPI (Combined)", "GDP deflator", "IIP"], 1, "The target is set on CPI (Combined)."),
            q("Simple interest on ₹5,000 at 10% per year for 2 years is:", ["₹500", "₹1,000", "₹1,050", "₹1,500"], 1, "SI = 5000 × 10 × 2 ÷ 100 = ₹1,000."),
        ],
    },
    # ---------------------------------------------------------------- science
    "isro": {
        "modules": [
            m("physics", "Physics & mathematics", "Engineering fundamentals.",
              ["Mechanics", "Electromagnetism", "Thermodynamics", "Engineering maths"],
              [v("Engineering physics", "engineering physics basics for ISRO"), v("Engineering maths", "engineering mathematics for ISRO")]),
            m("space-tech", "Space technology", "Rockets, satellites and orbits.",
              ["Launch vehicles", "Orbital mechanics", "Satellite subsystems", "ISRO missions"],
              [v("ISRO missions", "ISRO missions explained"), v("Orbital mechanics", "orbital mechanics basics")]),
            m("core-branch", "Your core branch", "Electronics, mechanical, computer science.",
              ["Electronics & communication", "Mechanical design", "Computer science", "Control systems"],
              [v("ISRO exam prep", "ISRO scientist engineer exam preparation"), v("ECE for ISRO", "ISRO electronics previous year questions")]),
            m("aptitude", "Aptitude & interview", "Written test and technical interview.",
              ["Previous year papers", "Technical interview", "Resume basics", "Current space news"],
              [v("ISRO interview", "ISRO interview preparation"), v("ISRO papers", "ISRO previous year paper solution")]),
        ],
        "questions": [
            q("India's first satellite, launched in 1975, was:", ["Bhaskara", "Aryabhata", "INSAT-1A", "Rohini"], 1, "Aryabhata was India's first satellite."),
            q("ISRO's main launch centre is at:", ["Sriharikota", "Thumba", "Bengaluru", "Hyderabad"], 0, "Satish Dhawan Space Centre is at Sriharikota."),
            q("Earth's escape velocity is approximately:", ["7.9 km/s", "9.8 km/s", "11.2 km/s", "15 km/s"], 2, "Escape velocity from Earth is about 11.2 km/s."),
            q("The SI unit of force is the:", ["Joule", "Newton", "Pascal", "Watt"], 1, "Force is measured in newtons."),
            q("Chandrayaan-3 made a soft landing near the Moon's:", ["Equator", "North pole", "South polar region", "Far side centre"], 2, "It landed near the lunar south polar region in August 2023."),
        ],
    },
    "drdo": {
        "modules": [
            m("gate-core", "GATE / core subject", "Your engineering branch fundamentals.",
              ["Engineering maths", "Core branch subjects", "Previous GATE papers", "Problem solving"],
              [v("GATE strategy", "GATE preparation strategy"), v("Engineering maths", "GATE engineering mathematics")]),
            m("defence-tech", "Defence technologies", "What DRDO builds.",
              ["Missiles & propulsion", "Radar & electronics", "Aeronautics", "Materials"],
              [v("DRDO systems", "DRDO systems explained"), v("Indian missiles", "Indian missile programme explained")]),
            m("research", "Research aptitude", "Thinking like a scientist.",
              ["Scientific method", "Reading papers", "Lab basics", "Technical writing"],
              [v("Research basics", "how to read a research paper"), v("DRDO scientist", "how to become DRDO scientist")]),
            m("interview", "RAC interview", "Selection stages and interview.",
              ["Application & shortlisting", "Technical interview", "Current defence news", "Mock interviews"],
              [v("DRDO RAC", "DRDO RAC recruitment process"), v("Interview tips", "DRDO interview preparation")]),
        ],
        "questions": [
            q("DRDO was formed in:", ["1948", "1958", "1971", "1986"], 1, "DRDO was established in 1958."),
            q("The Agni series of missiles are:", ["Cruise missiles", "Surface-to-air missiles", "Ballistic missiles", "Anti-tank missiles"], 2, "Agni missiles are ballistic missiles."),
            q("Ohm's law states:", ["V = IR", "P = VI²", "F = ma", "E = mc²"], 0, "Voltage equals current times resistance."),
            q("GATE stands for:", ["General Aptitude Test for Engineers", "Graduate Aptitude Test in Engineering", "Government Admission Test for Employment", "Graduate Assessment Test for Experts"], 1, "GATE = Graduate Aptitude Test in Engineering."),
            q("The Tejas is India's indigenous:", ["Main battle tank", "Light combat aircraft", "Submarine", "Aircraft carrier"], 1, "Tejas is a light combat aircraft."),
        ],
    },
    # ------------------------------------------------------------ engineering
    "ese": {
        "modules": [
            m("gs-eng", "General studies & engineering aptitude", "Paper 1 of the prelims.",
              ["Current affairs", "Engineering aptitude", "Basic maths & reasoning", "Environment & ethics"],
              [v("ESE paper 1", "UPSC ESE general studies paper 1"), v("ESE strategy", "UPSC ESE preparation strategy")]),
            m("mechanics", "Strength of materials & mechanics", "Common to most branches.",
              ["Stress & strain", "Beams & bending", "Fluid mechanics", "Thermodynamics"],
              [v("Strength of materials", "strength of materials for ESE"), v("Fluid mechanics", "fluid mechanics for ESE GATE")]),
            m("branch", "Your branch subjects", "Civil, mechanical, electrical or E&T.",
              ["Core theory", "Numerical practice", "Design basics", "Previous year papers"],
              [v("ESE previous papers", "UPSC ESE previous year paper solution"), v("Branch notes", "ESE branch wise preparation")]),
            m("interview", "Personality test", "Final stage interview.",
              ["DAF preparation", "Technical questions", "Current issues", "Mock interviews"],
              [v("ESE interview", "UPSC ESE interview preparation"), v("DAF tips", "UPSC DAF preparation")]),
        ],
        "questions": [
            q("The SI unit of stress is:", ["Newton", "Pascal", "Joule", "Watt"], 1, "Stress is force per unit area: pascal (N/m²)."),
            q("Hooke's law holds good:", ["Beyond the yield point", "Within the elastic limit", "At fracture", "Only for liquids"], 1, "Stress is proportional to strain within the elastic limit."),
            q("Concrete is generally:", ["Strong in tension, weak in compression", "Strong in compression, weak in tension", "Equally strong in both", "Weak in both"], 1, "Concrete is strong in compression and weak in tension, hence reinforcement."),
            q("Bernoulli's principle relates:", ["Pressure, velocity and height in fluid flow", "Heat and work", "Voltage and current", "Mass and energy"], 0, "It relates pressure, velocity and elevation in flowing fluids."),
            q("The second law of thermodynamics concerns:", ["Conservation of mass", "Direction of heat flow and entropy", "Atomic structure", "Electric charge"], 1, "It states heat flows from hot to cold and entropy increases."),
        ],
    },
    # ----------------------------------------------------------------- health
    "doctor": {
        "modules": [
            m("anatomy-physio", "Anatomy & physiology", "How the body is built and works.",
              ["Body systems", "Cardiovascular & respiratory", "Nervous system", "Endocrine system"],
              [v("Human physiology", "human physiology NEET"), v("Anatomy basics", "human anatomy basics")]),
            m("biochem", "Biology & biochemistry", "NEET Biology foundations.",
              ["Cell biology", "Genetics", "Biomolecules", "Human health & disease"],
              [v("NEET biology", "NEET biology full course"), v("Biomolecules", "biomolecules NEET")]),
            m("chem-phy", "Chemistry & physics for NEET", "The other two NEET subjects.",
              ["Organic chemistry", "Physical chemistry", "Mechanics & optics", "Modern physics"],
              [v("NEET chemistry", "NEET chemistry preparation"), v("NEET physics", "NEET physics preparation")]),
            m("public-health", "Public health & recruitment", "Working in public hospitals.",
              ["National health programmes", "Epidemiology basics", "Medical ethics", "State recruitment exams"],
              [v("Public health", "public health India basics"), v("Govt doctor jobs", "government medical officer recruitment")]),
        ],
        "questions": [
            q("The largest organ of the human body is the:", ["Liver", "Skin", "Lungs", "Brain"], 1, "The skin is the largest organ."),
            q("A normal adult resting heart rate is about:", ["30–50 bpm", "60–100 bpm", "110–140 bpm", "150–180 bpm"], 1, "Typically 60–100 beats per minute."),
            q("Scurvy is caused by deficiency of vitamin:", ["A", "B12", "C", "D"], 2, "Scurvy results from vitamin C deficiency."),
            q("Which hormone lowers blood glucose?", ["Glucagon", "Insulin", "Adrenaline", "Thyroxine"], 1, "Insulin lowers blood glucose."),
            q("Tuberculosis is caused by:", ["Mycobacterium tuberculosis", "Plasmodium", "Vibrio cholerae", "Salmonella typhi"], 0, "TB is caused by Mycobacterium tuberculosis."),
        ],
    },
    # -------------------------------------------------------------- education
    "teacher": {
        "modules": [
            m("child-dev", "Child development & pedagogy", "Core of CTET Paper 1 and 2.",
              ["Piaget, Vygotsky, Kohlberg", "Learning theories", "Inclusive education", "Assessment"],
              [v("CTET pedagogy", "CTET child development and pedagogy"), v("Learning theories", "CTET learning theories")]),
            m("languages", "Language I & II", "Hindi/English comprehension and pedagogy.",
              ["Comprehension", "Grammar", "Language pedagogy", "Teaching methods"],
              [v("CTET English", "CTET English pedagogy"), v("CTET Hindi", "CTET Hindi pedagogy")]),
            m("subject", "Maths, EVS or your subject", "Content and teaching methods.",
              ["Number system & geometry", "Environmental studies", "Science or social studies", "Teaching aids"],
              [v("CTET maths", "CTET maths pedagogy"), v("CTET EVS", "CTET EVS preparation")]),
            m("kvs-nvs", "KVS / NVS selection", "Recruitment specifics.",
              ["Exam pattern", "Interview & demo class", "NEP 2020 basics", "Previous papers"],
              [v("KVS preparation", "KVS teacher exam preparation"), v("NEP 2020", "NEP 2020 for teachers explained")]),
        ],
        "questions": [
            q("CTET is conducted by:", ["UGC", "NCERT", "CBSE", "NCTE"], 2, "CBSE conducts the Central Teacher Eligibility Test."),
            q("Under NEP 2020, the school structure is:", ["10+2", "5+3+3+4", "6+3+3", "8+4"], 1, "NEP 2020 replaces 10+2 with 5+3+3+4."),
            q("The stages of cognitive development were proposed by:", ["Skinner", "Pavlov", "Piaget", "Maslow"], 2, "Jean Piaget proposed four stages."),
            q("The Right to Education Act covers children aged:", ["3–10", "6–14", "5–16", "6–18"], 1, "RTE guarantees free education for ages 6–14."),
            q("Formative assessment is mainly meant to:", ["Rank students at year end", "Give ongoing feedback during learning", "Decide promotions only", "Replace teaching"], 1, "It is continuous feedback that guides learning."),
        ],
    },
    # -------------------------------------------------------------------- law
    "judge": {
        "modules": [
            m("constitution", "Constitutional law", "Foundation of every judicial exam.",
              ["Fundamental Rights", "Directive Principles", "Writs", "Union & State judiciary"],
              [v("Constitutional law", "constitutional law for judiciary exam"), v("Writs", "writs in Indian constitution explained")]),
            m("criminal", "Criminal law & procedure", "New criminal codes and procedure.",
              ["Bharatiya Nyaya Sanhita", "BNSS procedure", "Bharatiya Sakshya Adhiniyam", "Landmark cases"],
              [v("BNS overview", "Bharatiya Nyaya Sanhita overview"), v("Criminal procedure", "BNSS criminal procedure judiciary exam")]),
            m("civil", "Civil law & procedure", "Property, contract and CPC.",
              ["Code of Civil Procedure", "Contract Act", "Transfer of Property", "Limitation Act"],
              [v("CPC basics", "Code of Civil Procedure judiciary exam"), v("Contract Act", "Indian Contract Act judiciary exam")]),
            m("language-gk", "Language, GK & mains writing", "Judgement and answer writing.",
              ["Legal English", "Current legal affairs", "Judgement writing", "State-specific laws"],
              [v("Judiciary strategy", "judicial services exam strategy"), v("Judgement writing", "judgement writing judiciary mains")]),
        ],
        "questions": [
            q("Article 14 of the Constitution guarantees:", ["Freedom of religion", "Equality before law", "Right to education", "Protection against arrest"], 1, "Article 14 guarantees equality before the law."),
            q("Which writ is issued against illegal detention?", ["Mandamus", "Certiorari", "Habeas corpus", "Quo warranto"], 2, "Habeas corpus produces the detained person before the court."),
            q("The Indian Penal Code was replaced by the:", ["Bharatiya Nyaya Sanhita, 2023", "Indian Criminal Code, 2020", "Bharatiya Dand Adhiniyam, 2021", "Criminal Justice Act, 2019"], 0, "The BNS replaced the IPC with effect from 1 July 2024."),
            q("Article 32 gives the right to:", ["Property", "Constitutional remedies", "Free education", "Vote"], 1, "Article 32 is the right to move the Supreme Court for enforcement of rights."),
            q("The highest court of appeal in India is the:", ["High Court", "Supreme Court", "District Court", "Privy Council"], 1, "The Supreme Court is the final court of appeal."),
        ],
    },
}


def modules_for(career_id: str) -> list[dict]:
    return STUDY.get(career_id, {}).get("modules", [])


def questions_for(career_id: str) -> list[dict]:
    return STUDY.get(career_id, {}).get("questions", [])


def grade(career_id: str, answers: list[int | None]) -> dict:
    """Score a submission. Missing/invalid answers count as wrong."""
    qs = questions_for(career_id)
    results, score = [], 0
    for i, item in enumerate(qs):
        given = answers[i] if i < len(answers) else None
        ok = given == item["answer"]
        score += ok
        results.append({"correct": ok, "your_answer": given, "answer": item["answer"], "why": item["why"]})
    return {"score": score, "total": len(qs), "results": results}
