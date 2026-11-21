"""Static catalogue: sectors and careers (same content as the frontend)."""

SECTORS = [
    {"id": "civil", "name": "Civil services", "icon": "🏛", "sub": "Lead & serve communities"},
    {"id": "defence", "name": "Defence", "icon": "✈️", "sub": "Serve with courage"},
    {"id": "banking", "name": "Banking & finance", "icon": "📊", "sub": "Build financial futures"},
    {"id": "science", "name": "Science & technology", "icon": "🔬", "sub": "Discover what’s next"},
    {"id": "engineering", "name": "Engineering", "icon": "⚙️", "sub": "Design practical solutions"},
    {"id": "health", "name": "Healthcare", "icon": "🩺", "sub": "Make a difference"},
    {"id": "education", "name": "Education", "icon": "📚", "sub": "Shape future minds"},
    {"id": "law", "name": "Law & justice", "icon": "⚖️", "sub": "Uphold what is right"},
]

CAREERS = [
    {
        "id": "ias", "title": "Indian Administrative Service", "sector": "civil",
        "exam": "UPSC Civil Services Examination", "icon": "🏛", "match": 96,
        "desc": "Shape public policy and lead administration at district, state and national levels.",
        "eligibility": "Bachelor’s degree · Age 21–32",
    },
    {
        "id": "ifs", "title": "Indian Foreign Service", "sector": "civil",
        "exam": "UPSC Civil Services Examination", "icon": "🌐", "match": 92,
        "desc": "Represent India abroad and work across diplomacy, trade and international relations.",
        "eligibility": "Bachelor’s degree · Age 21–32",
    },
    {
        "id": "nda", "title": "National Defence Academy", "sector": "defence",
        "exam": "UPSC NDA & NA Examination", "icon": "✈️", "match": 89,
        "desc": "Begin a leadership career as an officer in the Army, Navy or Air Force.",
        "eligibility": "Class 12 · Age 16.5–19.5",
    },
    {
        "id": "rbi", "title": "RBI Grade B Officer", "sector": "banking",
        "exam": "RBI Grade B Examination", "icon": "📈", "match": 87,
        "desc": "Contribute to India’s monetary policy, financial regulation and economic stability.",
        "eligibility": "Bachelor’s degree · Age 21–30",
    },
    {
        "id": "isro", "title": "ISRO Scientist / Engineer", "sector": "science",
        "exam": "ISRO Centralised Recruitment", "icon": "🛰️", "match": 94,
        "desc": "Work on satellite, launch vehicle and space science missions with India’s space agency.",
        "eligibility": "Relevant engineering degree",
    },
    {
        "id": "drdo", "title": "DRDO Scientist", "sector": "science",
        "exam": "RAC Recruitment / GATE", "icon": "🧪", "match": 90,
        "desc": "Research and develop technologies that support India’s defence and national security.",
        "eligibility": "Engineering / postgraduate degree",
    },
    {
        "id": "ese", "title": "Engineering Services Officer", "sector": "engineering",
        "exam": "UPSC Engineering Services Exam", "icon": "⚙️", "match": 84,
        "desc": "Lead public infrastructure and engineering projects across central government services.",
        "eligibility": "Engineering degree · Age 21–30",
    },
    {
        "id": "doctor", "title": "Government Medical Officer", "sector": "health",
        "exam": "NEET · State / Central recruitment", "icon": "🩺", "match": 86,
        "desc": "Deliver essential medical care through public hospitals and community health systems.",
        "eligibility": "MBBS · Relevant registration",
    },
    {
        "id": "teacher", "title": "Central Government Teacher", "sector": "education",
        "exam": "CTET / KVS / NVS recruitment", "icon": "📚", "match": 81,
        "desc": "Inspire students and create strong learning foundations in government schools.",
        "eligibility": "Teaching qualification · CTET",
    },
    {
        "id": "judge", "title": "Judicial Services Officer", "sector": "law",
        "exam": "State Judicial Services Exam", "icon": "⚖️", "match": 82,
        "desc": "Serve the justice system and help uphold the rule of law in your state.",
        "eligibility": "LLB · State eligibility",
    },
]
