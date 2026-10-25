"""Deterministic extractor used when the LLM is disabled.

Table-driven regex/keyword heuristics for English, Hinglish, Hindi and Marathi offers.
Precision over recall: a field stays null when unsure. Text is untrusted data; lines that
read like instructions to a model are skipped and nothing in the text changes behaviour.
Values follow docs/CONTRACTS.md; every quote is a verbatim substring of its source text.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal

from .models import FieldValue, Offer, SourceRef

_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")  # 1:1, so offsets match the original
MAX_LINES = 20000
MAX_LINE_CHARS = 5000


def rx(*alts: str, flags: int = re.I) -> re.Pattern:
    return re.compile("|".join(alts), flags)


# ---------------------------------------------------------------- amounts
_CUR = {  # token regex -> ISO code
    r"₹|(?<![a-z])rs\.?(?![a-z])|(?<![a-z])inr(?![a-z])|rupees?|रुपये|रुपया|रूपये|रुपए|रु\.?|रू\.?": "INR",
    r"(?<![a-z])aed(?![a-z])|dirhams?|(?<![a-z])dhs?(?![a-z])|दिरहम|दिरहाम": "AED",
    r"(?<![a-z])sar(?![a-z])|riyals?|रियाल": "SAR",
    r"(?<![a-z])thb(?![a-z])|baht|बाहट|भात": "THB",
    r"(?<![a-z])usd(?![a-z])|\$|dollars?|डॉलर|डालर": "USD",
    r"(?<![a-z])qar(?![a-z])": "QAR", r"(?<![a-z])kwd(?![a-z])": "KWD",
    r"(?<![a-z])omr(?![a-z])": "OMR", r"(?<![a-z])myr(?![a-z])|ringgit": "MYR",
    r"(?<![a-z])sgd(?![a-z])": "SGD", r"(?<![a-z])eur(?![a-z])|€": "EUR",
}
_CUR_RE = "|".join(f"(?:{k})" for k in _CUR)
_MULT = {  # token regex -> multiplier
    r"lakhs?(?![a-z])|lacs?(?![a-z])|लाख": 100000,
    r"crores?(?![a-z])|cr(?![a-z])|करोड़|करोड": 10000000,
    r"hazaar(?![a-z])|hazar(?![a-z])|hajar(?![a-z])|thousand(?![a-z])|हजार|हज़ार|k(?![a-z])": 1000,
}
_MULT_RE = "|".join(f"(?:{k})" for k in _MULT)
_WORD_NUM = {"अडीच": "2.5", "अढाई": "2.5", "ढाई": "2.5", "अढ़ाई": "2.5", "दीड": "1.5", "डेढ़": "1.5", "डेढ": "1.5",
             "सव्वा": "1.25", "पाऊण": "0.75", "पौन": "0.75", "एक": "1", "दो": "2", "दोन": "2", "तीन": "3",
             "चार": "4", "पाच": "5", "पांच": "5", "पाँच": "5", "सहा": "6", "छह": "6", "सात": "7", "आठ": "8",
             "नऊ": "9", "नौ": "9", "दस": "10", "दहा": "10"}
_HALF = r"साढ़े|साडे|साढे|साड़े"
_NUM = r"\d[\d,]*(?:\.\d+)?"
_AMOUNT = re.compile(
    rf"(?P<c1>{_CUR_RE})?\s*(?P<half>{_HALF})?\s*(?:(?P<num>{_NUM})|(?P<word>{'|'.join(sorted(_WORD_NUM, key=len, reverse=True))}))\s*(?P<mult>{_MULT_RE})?\s*(?P<c2>{_CUR_RE})?",
    re.I)


@dataclass(frozen=True)
class Amount:
    value: Decimal
    currency: str | None  # ISO code; INR is implied by lakh/crore/hazar without another currency


def _currency(token: str | None) -> str | None:
    for pattern, iso in _CUR.items():
        if token and re.fullmatch(pattern, token, re.I):
            return iso
    return None


def _multiplier(token: str) -> int:
    return next(v for k, v in _MULT.items() if re.fullmatch(k, token, re.I))


def parse_amounts(text: str, bare: bool = False) -> list[Amount]:
    """Amounts in `text`: '2.5 lakh', 'अडीच लाख', '२,५०,०००', 'Rs 30,000 + GST'.

    A number counts only with a currency or lakh/crore/hazar marker, unless `bare` (then
    plain numbers of 1000+ with fewer than 8 digits also count, which skips phone numbers).
    """
    out = []
    for m in _AMOUNT.finditer(text.translate(_DIGITS)):
        mult = _multiplier(m["mult"]) if m["mult"] else 1
        cur = _currency(m["c1"] or m["c2"])
        if m["word"]:
            if not m["mult"]:
                continue  # 'दो' alone is not money
            base = Decimal(_WORD_NUM[m["word"]]) + (Decimal("0.5") if m["half"] else 0)
        else:
            digits = m["num"].rstrip(",").replace(",", "")
            if len(digits.split(".")[0]) >= 8 and not m["mult"]:
                continue
            base = Decimal(digits) + (Decimal("0.5") if m["half"] and m["mult"] else 0)
            if not (m["mult"] or cur or (bare and base * mult >= 1000)):
                continue
        out.append(Amount((base * mult).normalize(), cur or ("INR" if m["mult"] else None)))
    return out


def amount_values(text: str, bare: bool = True) -> set[Decimal]:
    return {a.value for a in parse_amounts(text, bare)}


def _num_str(value: Decimal) -> str:
    return format(value, "f").rstrip("0").rstrip(".") if "." in format(value, "f") else format(value, "f")


# ---------------------------------------------------------------- lexicons
FEE_STRONG = rx(r"\bfees?\b", r"processing", r"\bcharges?\b", r"deposit", r"शुल्क", r"फी",r"फीस", r"चार्ज", r"डिपॉ[झज]िट")
FEE_WEAK = rx(r"\btotal\b", r"कुल", r"एकूण", r"\bpay(?:ment|able)?\b", r"\bsend\b", r"bhej", r"भेज", r"पाठव", r"transfer", r"\bupi\b", r"g\s?pay", r"phone\s*pe",
              r"paytm", r"\bcash\b", r"नकद", r"रोख", r"\bneft\b", r"\bimps\b",r"advance", r"booking", r"\btoken\b", r"commission", r"भरा", r"भराव", r"देना", r"द्यावे",
              r"द्यावा", r"लागेल", r"लगेगा", r"लगेंगे", r"पैसे", r"रक्कम", r"\bcost\b")
SAL_STRONG = rx(r"salary", r"pag[ao]?ar", r"\bwages?\b", r"earn", r"वेतन", r"पगार", r"तनख", r"तन्ख", r"कमाई", r"कमव", r"tankh")
SAL_WEAK = rx(r"per month", r"\ba month\b", r"/\s*month", r"monthly", r"\bp\.?m\b", r"mahin[ae]", r"महीन", r"महिन", r"मासिक", r"प्रति माह")
CLAUSE_SPLIT = re.compile(r",\s|;|(?<![Rr][Ss])(?<![Nn][Oo])\.\s+|।\s*|\|\s|\s(?:and|aur|but|lekin)\s|\s(?:और|आणि|व|पण|लेकिन)\s", re.I)

VISA = r"(?:visa|वीजा|वीसा|व्हिसा|वीज़ा|विजा)"
VISA_TYPES = [  # (type, word before/after the word visa)
    ("tourist", r"(?:tourist|tourism|पर्यटक|पर्यटन|टूरिस्ट|टुरिस्ट)"),
    ("visit", r"(?:visit(?:or)?|विज़िट|विजिट|व्हिजिट)"),
    ("employment", r"(?:employment|rozgar|job|रोजगार|रोज़गार|नोकरी|नौकरी)"),
    ("work", r"(?:work(?:ing)?|वर्क|कार्य)"),
]
NEGATION = rx(r"\b(?:not|no|never|isn'?t|nahi|nahin|nhi)\b", r"नहीं", r"नही", r"नाही", r"नको", r"नका")
NEG_BEFORE = re.compile(r"(?:^|\s)(?:not|no|never|isn'?t|nahi|nahin|नहीं|नही|नाही|नको|नका)\s+(?:\S+\s+){0,2}$", re.I)
NEG_AFTER = re.compile(r"^\s*(?:\S+\s+){0,2}?(?:nahi|nahin|नहीं|नही|नाही)(?!\S)", re.I)

IT_WORD = re.compile(r"(?<![A-Za-z0-9])I\.?T\.?(?![A-Za-z0-9])|आईटी|आयटी")  # case-sensitive: not the pronoun "it"
IT_NEXT = [("technician", r"technician|तकनीशियन|तंत्रज्ञ"), ("support", r"support|सपोर्ट"), ("engineer", r"engineer|इंजीनियर|अभियंता"),
           ("specialist", r"specialist")]
HIGH_RISK_ROLE_COUNT = 5  # the first N entries of ROLES outrank IT and the rest
ROLES = {  # high-risk roles first: the first role that matches on a line wins
    "data entry": [r"data\s*entry", r"डेटा\s*एं?न?्?ट्री", r"डाटा\s*एं?न?्?ट्री"],
    "chat support": [r"chat\s*support", r"चै?ट\s*सपोर्ट", r"चॅट\s*सपोर्ट"],
    "digital marketing": [r"digital\s*marketing", r"डिजिटल\s*मार्केटिंग"],
    "online marketing": [r"online\s*marketing", r"ऑनलाइन\s*मार्केटिंग"],
    "customer support": [r"customer\s*(?:support|service|care)", r"call\s*cent(?:er|re)", r"कस्टमर\s*(?:सपोर्ट|सर्विस|केयर)",
                         r"ग्राहक\s*(?:सहायता|सेवा|सपोर्ट)"],
    "telecaller": [r"tele\s*caller", r"टेलीकॉलर", r"टेलिकॉलर"],
    "electrician": [r"electrician", r"इलेक्ट्रीशियन", r"इलेक्ट्रिशियन"],
    "plumber": [r"plumber", r"प्लंबर"],
    "welder": [r"welder", r"वेल्डर"],
    "driver": [r"driver", r"ड्राइवर", r"ड्रायव्हर", r"चालक"],
    "cook": [r"cook", r"chef", r"कुक", r"शेफ", r"बावर्ची"],
    "security guard": [r"security\s*guard", r"सिक्योरिटी\s*गार्ड", r"सिक्युरिटी\s*गार्ड", r"वॉचमन"],
    "nurse": [r"nurse", r"नर्स"],
    "helper": [r"helper", r"हेल्पर"],
    "carpenter": [r"carpenter", r"बढ़ई", r"सुतार"],
    "mason": [r"mason", r"राजमिस्त्री"],
    "construction worker": [r"construction\s*worker", r"कंस्ट्रक्शन"],
    "warehouse worker": [r"warehouse", r"वेयरहाउस"],
    "housekeeping": [r"house\s*keeping", r"cleaner", r"हाउसकीपिंग"],
    "hotel staff": [r"hotel\s*(?:staff|jobs?)", r"हॉटेल\s*स्टाफ", r"होटल\s*स्टाफ"],
    "technician": [r"technician", r"टेक्निशियन", r"तंत्रज्ञ"],
    "mechanic": [r"mechanic", r"मैकेनिक", r"मेकॅनिक"],
    "labourer": [r"labou?rer", r"मजदूर", r"मजूर"],
    "typist": [r"typist", r"टाइपिस्ट"],
}
ROLE_LABEL = re.compile(r"(?:position|post|role|designation|vacancy|पद|पोस्ट)\s*[:\-]\s*([^,;.।\n(]{3,40})", re.I)

COUNTRIES = {
    "Thailand": ["thailand", "bangkok", "pattaya", "phuket", "mae sot", "chiang mai", "थाईलैंड", "थायलंड", "थाईलॅंड",
                 "थाइलैंड", "बैंकॉक", "बँकॉक", "पटाया"],
    "Myanmar": ["myanmar", "burma", "yangon", "myawaddy", "म्यानमार", "म्यांमार", "म्यांमर", "यांगून", "म्यावड्डी"],
    "Cambodia": ["cambodia", "phnom penh", "sihanoukville", "poipet", "कंबोडिया", "कम्बोडिया", "कंबोडीया"],
    "Laos": ["laos", "vientiane", "लाओस", "वियनतियाने", "विएंतियान"],
    "Vietnam": ["vietnam", "वियतनाम", "व्हिएतनाम"],
    "United Arab Emirates": ["uae", "u.a.e", "dubai", "abu dhabi", "sharjah", "united arab emirates", "दुबई", "अबू धाबी",
                             "यूएई", "संयुक्त अरब अमीरात", "शारजाह"],
    "Saudi Arabia": ["saudi", "riyadh", "jeddah", "dammam", "सौदी", "सऊदी", "रियाध", "जेद्दा"],
    "Qatar": ["qatar", "doha", "कतर", "कतार"],
    "Oman": ["oman", "muscat", "ओमान", "मस्कत"],
    "Kuwait": ["kuwait", "कुवैत"],
    "Bahrain": ["bahrain", "बहरीन"],
    "Malaysia": ["malaysia", "kuala lumpur", "मलेशिया", "मलेसिया"],
    "Singapore": ["singapore", "सिंगापूर", "सिंगापुर"],
    "Russia": ["russia", "रशिया", "रूस", "रुस"],
    "Israel": ["israel", "इस्रायल", "इजराइल", "इज़राइल"],
}
_PLACE = [(re.compile((rf"(?<![A-Za-z]){re.escape(a)}(?![A-Za-z])" if a.isascii() else re.escape(a)), re.I), c)
          for c, aliases in COUNTRIES.items() for a in aliases]
_TRANSIT_BEFORE = re.compile(r"(?:\bvia|\bthrough|\bthru|\btransit(?:ing)?(?:\s+(?:in|via|through))?|\bby way of)\W*(?:the\s+)?$", re.I)
_TRANSIT_AFTER = re.compile(r"\s*(?:से\s*होकर|के\s*रास्ते|के\s*माध्यम|के\s*मार्गे|मार्गे|मार्गाने|होकर|वरून|(?:ke\s+)?(?:through|via|raste|se\s*ho\s*kar|ho\s*kar))", re.I)

PAYMENT = [  # first match wins
    ("upi", rx(r"\bupi\b", r"g\s?pay", r"google\s*pay", r"phone\s*pe", r"paytm", r"\bbhim\b", r"यूपीआई")),
    ("crypto", rx(r"crypto", r"bitcoin", r"\busdt\b", r"क्रिप्टो")),
    ("bank_transfer", rx(r"\bneft\b", r"\bimps\b", r"\brtgs\b", r"bank\s*(?:transfer|account|a/c)", r"बैंक\s*(?:खाते|खात्यात|में|ट्रांसफर|अकाउंट)", r"खात्यात")),
    ("card", rx(r"(?:credit|debit)\s*card", r"\bcard\b")),
    ("cash", rx(r"\bcash\b", r"नकद", r"रोख", r"कैश")),
    ("other", rx(r"western\s*union", r"hawala", r"हवाला")),
]
RECEIPT = rx(r"receipt", r"रसीद", r"पावती", r"रिसीट", r"rasid")
CONTRACT = rx(r"contract", r"agreement", r"अनुबंध", r"करार", r"कॉन्ट्रैक्ट", r"कॉन्ट्रॅक्ट", r"एग्रीमेंट")
SIGN = rx(r"\bsign", r"हस्ताक्षर", r"स्वाक्षरी", r"दस्तखत", r"सही")
SIGNATORIES = [("employer", rx(r"employer", r"\bcompany\b", r"कंपनी", r"नियोक्ता", r"मालक", r"मालिक")),
               ("agent", rx(r"agent", r"agency", r"एजेंट", r"एजंट", r"एजेंसी")),
               ("worker", rx(r"worker", r"employee", r"candidate", r"कामगार", r"कर्मचारी", r"उम्मीदवार", r"मजदूर", r"कामकरी"))]
PBBY = rx(r"\bpbby\b", r"pravasi\s*bharatiya\s*bima", r"insurance", r"प्रवासी\s*भारतीय\s*(?:बीमा|विमा)", r"बीमा", r"विमा", r"विम्य")
PASSPORT = rx(r"passport", r"पासपोर्ट")
HANDOVER = rx(r"jama", r"submit", r"hand\s*over", r"\bgive\b", r"surrender", r"deposit", r"\bkeep\b", r"\bhold\b", r"collect",
              r"जमा", r"सौंप", r"सुपूर्द", r"द्या", r"ठेवू", r"रखेंगे", r"रखना", r"रखू", r"भेज", r"\bsend\b")
PASSPORT_COPY = rx(r"copy", r"photo", r"scan", r"कॉपी", r"प्रत", r"फोटो")
PASSPORT_NO = rx(r"do not", r"don'?t", r"\bnever\b", r"no need", r"\bmat\b", r"नका", r"नको", r"मत\s")
URGENCY = rx(r"today only", r"(?:confirm|pay|book|decide)\s+today", r"only today", r"only\s+\d+\s+(?:seats?|slots?|vacanc\w+|posts?)(?:\s+left)?",
             r"(?:last|few)\s+(?:few\s+)?(?:seats?|slots?|chance)", r"limited\s+(?:seats?|slots?|time)", r"\bhurry\b",
             r"\burgent(?:ly)?\b", r"immediately", r"book now", r"offer ends?", r"\bjaldi\b", r"\bturant\b", r"\baajach\b",
             r"आज\s*ही", r"आजच", r"जल्दी", r"लगेच", r"तुरंत", r"अंतिम\s*(?:सीट|मौका|तारीख)", r"आखिरी\s*(?:सीट|मौका)",
             r"(?:सिर्फ|केवल|फक्त)\s*\d+\s*(?:सीट|जागा|जगह)\w*", r"शेवटच्या\s*\w+", r"शेवटची\s*संधी", r"उरल्या\s*\w*")
CHANNELS = [
    ("whatsapp", rx(r"whats\s*app", r"watsapp", r"wa\.me", r"व्हाट्सएप", r"व्हॉट्सअॅप", r"व्हॉट्सॲप", r"व्हाट्सऐप", r"वॉट्सअप", r"व्हाट्सअप")),
    ("telegram", rx(r"telegram", r"t\.me/", r"टेलीग्राम", r"टेलिग्राम")),
    ("instagram", rx(r"instagram", r"\binsta\b", r"इंस्टाग्राम")),
    ("facebook", rx(r"facebook", r"fb\.com", r"फेसबुक")),
    ("email", rx(r"[\w.+-]+@[\w-]+\.[\w.]+", r"\be-?mail\b", r"ईमेल")),
    ("website", rx(r"https?://", r"\bwww\.", r"(?<![@\w.-])[\w-]+\.(?:com|in|org|net)\b(?!/?\w*@)")),
    ("office_address", rx(r"\boffice\s*[:\-]", r"\baddress\b", r"पत्ता", r"पता\s*[:\-]", r"कार्यालय")),
]
PHONE_CTX = rx(r"\bcall\b", r"\bphone\b", r"कॉल", r"फोन")
ADDRESS_WORDS = rx(r"office", r"floor", r"road", r"\bstreet\b", r"nagar", r"plaza", r"building", r"मजला", r"मंजिल", r"रोड", r"नगर")
PIN = re.compile(r"(?<!\d)[1-9]\d{5}(?!\d)")
PHONE_INTL = re.compile(r"(?<![\w])\+\s?\d[\d\s\-()]{8,16}\d")
PHONE_IN = re.compile(r"(?<![\d,.+])(?:91[\s-]?|0)?([6-9]\d{4}[\s-]?\d{5})(?![\d,])")
RC_SHAPE = re.compile(r"(?<![A-Za-z0-9])[A-Z]-\d{3,5}(?:/[A-Za-z0-9+.\-]+)+")
RC_LABEL = re.compile(
    r"(?:\bRC\b|\bR\.C\.|\bRA\b|licen[cs]e|registration|\breg\b\.?|लायसन्स|लायसेंस|लाइसेंस|लाईसेन्स|लाइसन्स|परवाना|पंजीकरण|नोंदणी|रजिस्ट्रेशन)\s*"
    r"(?:no\.?|number|क्रमांक|क्र\.?|नंबर|संख्या)?\s*[:\-#]?\s*([A-Z0-9][A-Za-z0-9/\-+.]{3,})", re.I)
_ORG = r"(?:[A-Z][A-Za-z0-9&.'\-]*\s+)"
AGENT_NAME = re.compile(rf"\b({_ORG}{{1,4}}(?:Overseas|Placements?|Recruitment|Manpower|Consultancy|Consultants|Immigration|Agency)"
                        r"(?:\s+(?:Placements?|Services|Consultants|Pvt\.?|Ltd\.?|India))*)")
AGENT_LABEL = re.compile(r"(?i:\bagent|\bagency|एजेंट|एजंट|एजेंसी)(?i:\s*name|\s*नाम)?\s*[:\-]\s*([A-Z][^,;\n(]{2,50})")
EMPLOYER_NAME = re.compile(rf"\b({_ORG}{{1,5}}(?:LLC|L\.L\.C\.?|Ltd\.?|Limited|FZE|FZCO|FZ-LLC|Pte|Co\.|Company|Trading|Group|"
                           r"Corporation|Inc\.?|Industries|Hotels?|Resorts?))")
EMPLOYER_LABEL = re.compile(r"(?i:employer|company|कंपनी|नियोक्ता)\s*[:\-]\s*([A-Z][^,;\n(]{2,50})")
WA_PREFIX = re.compile(r"^\[?\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:[APap]\.?[Mm]\.?)?\]?\s*(?:-\s*)?[^:\n]{1,60}:\s+")


# ---------------------------------------------------------------- pipeline
@dataclass(frozen=True)
class Unit:
    text: str  # verbatim line body (what we quote)
    norm: str  # same length, Devanagari digits ASCII
    ref: str


def _units(sources: list[SourceRef]) -> list[Unit]:
    """Per-line/page sources first, base copies last; identical bodies counted once.

    Instruction-like text is never a reason to drop a line: the extractor cannot be instructed,
    and dropping lines would let a sender hide red flags.
    """
    ordered = sorted(sources, key=lambda s: s.line is None and s.page is None)
    seen, units = set(), []
    for s in ordered:
        for raw in s.text.splitlines():
            body = raw.strip()
            m = WA_PREFIX.match(body)
            body = body[m.end():].strip() if m else body
            if not body or len(body) > MAX_LINE_CHARS or body in seen:
                continue
            seen.add(body)
            units.append(Unit(body, unicodedata.normalize("NFC", body.translate(_DIGITS)), s.id))
            if len(units) >= MAX_LINES:
                return units
    return units


def _fv(value: str, unit: Unit) -> FieldValue:
    return FieldValue(value=value, quote=unit.text, source_ref=unit.ref, confidence="fallback")


def _first(units, finder):
    for u in units:
        v = finder(u)
        if v is not None:
            return _fv(v, u)
    return FieldValue()


def _all(units, finder) -> list[FieldValue]:
    out, seen = [], set()
    for u in units:
        for v in finder(u):
            if v not in seen:
                seen.add(v)
                out.append(_fv(v, u))
    return out


def _clauses(text: str):
    return CLAUSE_SPLIT.split(text)


def _visa(units):
    found = []
    for u in units:
        for clause in _clauses(u.norm):
            for kind, word in VISA_TYPES:
                for m in re.finditer(rf"{word}\s*{VISA}|{VISA}\s*(?:type)?\s*[:\-]\s*(?:an?\s+)?{word}", clause, re.I):
                    if not (NEG_BEFORE.search(clause[max(0, m.start() - 40):m.start()]) or NEG_AFTER.match(clause[m.end():m.end() + 40])):
                        found.append((kind, u))
    # tourist/visit anywhere wins over employment/work: the conservative reading for a safety check
    pick = next((f for f in found if f[0] in {"tourist", "visit"}), found[0] if found else None)
    return _fv(*pick) if pick else FieldValue()


def _money(units):
    """fee / salary amount and currency, classified per clause."""
    fee = sal = cur = None
    fee_best = Decimal(-1)
    for u in units:
        for clause in _clauses(u.norm):
            kind = ("salary" if SAL_STRONG.search(clause) else "fee" if FEE_STRONG.search(clause)
                    else "salary" if SAL_WEAK.search(clause) else "fee" if FEE_WEAK.search(clause) else None)
            if kind is None:
                continue
            amounts = parse_amounts(clause) or parse_amounts(clause, bare=True)
            if not amounts:
                continue
            a = amounts[0]
            if kind == "fee":  # largest INR fee wins: covers GST-inclusive totals and small "registration" fees
                for b in amounts:
                    if b.currency in (None, "INR") and b.value > fee_best:
                        fee_best, fee = b.value, _fv(_num_str(b.value), u)
            elif sal is None:
                sal = _fv(_num_str(a.value), u)
                if a.currency:
                    cur = _fv(a.currency, u)
    return fee or FieldValue(), sal or FieldValue(), cur or FieldValue()


def _role(u):
    for role, pats in list(ROLES.items())[:HIGH_RISK_ROLE_COUNT]:
        if any(re.search(p if not p.isascii() else rf"(?<![A-Za-z]){p}(?![A-Za-z])", u.norm, re.I) for p in pats):
            return role
    it = IT_WORD.search(u.norm)
    if it:
        nxt = u.norm[it.end():it.end() + 30]
        word = next((w for w, p in IT_NEXT if re.match(rf"\s*(?:{p})", nxt, re.I)), None)
        return f"it {word}" if word else "it"
    for role, pats in ROLES.items():
        if any(re.search(p if not p.isascii() else rf"(?<![A-Za-z]){p}(?![A-Za-z])", u.norm, re.I) for p in pats):
            return role
    m = ROLE_LABEL.search(u.norm)
    return m[1].strip().lower() if m else None


def _places(u):
    """[(country, is_transit)] in order of appearance."""
    hits = []
    for pat, country in _PLACE:
        for m in pat.finditer(u.norm):
            transit = bool(_TRANSIT_BEFORE.search(u.norm[max(0, m.start() - 25):m.start()])
                           or _TRANSIT_AFTER.match(u.norm, m.end()))
            hits.append((m.start(), country, transit))
    return [(c, t) for _, c, t in sorted(hits)]


def _destination(units):
    return _first(units, lambda u: next((c for c, t in _places(u) if not t), None))


def _transit(units):
    return _all(units, lambda u: [c for c, t in _places(u) if t])


def _payment(u):
    return next((mode for mode, p in PAYMENT if p.search(u.norm)), None)


_SENT = re.compile(r"(?:[^.।;?!\n]|(?<=[Rr][Ss])\.|(?<=[Nn][Oo])\.|\.(?=\d))+[.।;?!]?")


def _sentences(text: str):
    """Sentences of a line (questions dropped); negation is judged inside one sentence only."""
    return [m.group(0) for m in _SENT.finditer(text) if not m.group(0).rstrip().endswith("?")]


def _yes_no(pat, neg=NEGATION):
    def finder(u):
        for sent in _sentences(u.norm):
            if pat.search(sent):
                return "no" if neg.search(sent) else "yes"
        return None
    return finder


def _passport(u):
    for sent in _sentences(u.norm):
        if not PASSPORT.search(sent) or not HANDOVER.search(sent):
            continue
        if PASSPORT_COPY.search(sent) and not re.search(r"original|ओरिजिनल|मूळ|मूल|असली", sent, re.I):
            continue
        return "no" if PASSPORT_NO.search(sent) else "yes"
    return None


def _signatories(u):
    if not (CONTRACT.search(u.norm) and SIGN.search(u.norm)):
        return []
    return [who for who, p in SIGNATORIES if p.search(u.norm)]


def _urgency(u):
    return [m.group(0).strip() for m in URGENCY.finditer(u.norm)]


def _phones(u):
    out = []
    for m in PHONE_INTL.finditer(u.norm):
        out.append("+" + re.sub(r"\D", "", m.group(0)))
    rest = PHONE_INTL.sub(" ", u.norm)
    out += ["+91" + re.sub(r"\D", "", m[1]) for m in PHONE_IN.finditer(rest)]
    return out


def _channels(u):
    out = [name for name, p in CHANNELS if name != "office_address" and p.search(u.norm)]
    for sent in _sentences(u.norm):  # "no office address" / "कार्यालय नहीं" is not an office
        if NEGATION.search(sent):
            continue
        if dict(CHANNELS)["office_address"].search(sent) or (PIN.search(sent) and ADDRESS_WORDS.search(sent)):
            out.append("office_address")
            break
    if PHONE_CTX.search(u.norm) and _phones(u) and "phone" not in out:
        out.append("phone")
    return out


def _rc(u):
    m = RC_SHAPE.search(u.norm) or next((m for m in RC_LABEL.finditer(u.norm) if re.search(r"\d", m[1])), None)
    return (m.group(m.lastindex or 0) if m else "").rstrip(".,;)") or None


GENERIC_FIRST = {"Our", "The", "This", "That", "Your", "We", "Apply", "Contact", "Visit", "For", "In", "Only", "No",
                 "Recruitment", "Agency", "Agent"}


def _named(shape, label):
    def finder(u):
        m = label.search(u.norm) or shape.search(u.norm)
        v = m[1].strip().rstrip(".,") if m else None
        return v if v and v.split()[0] not in GENERIC_FIRST else None
    return finder


def extract(sources: list[SourceRef]) -> Offer:
    units = _units(sources)
    offer = Offer(source_ids=[s.id for s in sources])
    offer.visa_type = _visa(units)
    offer.fees_demanded_inr, offer.salary_amount, offer.salary_currency = _money(units)
    offer.role_title = _first(units, _role)
    offer.destination_country = _destination(units)
    offer.transit_countries = _transit(units)
    offer.fee_payment_mode = _first(units, _payment)
    offer.receipt_promised = _first(units, _yes_no(RECEIPT))
    offer.contract_mentioned = _first(units, _yes_no(CONTRACT))
    offer.contract_signatories = _all(units, _signatories)
    offer.pbby_insurance_mentioned = _first(units, _yes_no(PBBY))
    offer.passport_handover_requested = _first(units, _passport)
    offer.urgency_language = _all(units, _urgency)
    offer.agent_phones = _all(units, _phones)
    offer.agent_channels = _all(units, _channels)
    offer.agent_rc_number = _first(units, _rc)
    offer.agent_name = _first(units, _named(AGENT_NAME, AGENT_LABEL))
    employer = _first(units, _named(EMPLOYER_NAME, EMPLOYER_LABEL))
    offer.employer_name = employer if employer.value != offer.agent_name.value else FieldValue()
    return offer


_AGREE_FIELDS = {"visa_type", "destination_country", "fee_payment_mode", "receipt_promised", "contract_mentioned",
                 "pbby_insurance_mentioned", "passport_handover_requested", "salary_currency", "transit_countries",
                 "agent_channels", "contract_signatories", "role_title"}


def _dec(text: str):
    try:
        return Decimal(text.replace(",", ""))
    except Exception:
        return None


def supported_by_quote(name: str, value: str, quote: str) -> bool:
    """Deterministic check that a model-supplied value follows from its own quote.

    Enumerated fields must agree with what this module's lexicons find in the quote; free-text
    fields (names, RC number, phones, urgency) must literally appear in it.
    """
    q = unicodedata.normalize("NFC", quote.translate(_DIGITS))
    v = unicodedata.normalize("NFC", value.translate(_DIGITS)).strip()
    if name == "fees_demanded_inr":  # needs currency or lakh/hazar context, not a bare number
        return any(a.value == _dec(v) and a.currency in (None, "INR") for a in parse_amounts(q))
    if name == "salary_amount":
        return _dec(v) in amount_values(q)
    if name in _AGREE_FIELDS:
        offer = extract([SourceRef(id="Q", file="q", kind="quote", text=quote)])
        got = getattr(offer, name)
        found = {str(f.value).lower() for f in (got if isinstance(got, list) else [got])}
        return v.lower() in found or (name == "role_title" and v.lower() in q.lower())
    if name == "agent_phones":
        return re.sub(r"\D", "", v)[-10:] in re.sub(r"\D", "", q)
    return " ".join(v.split()).casefold() in " ".join(q.split()).casefold()
