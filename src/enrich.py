import re
import spacy
from duomenys import nuskaityti_fragmentus

nlp = spacy.load("lt_core_news_md", disable=["parser", "ner"])


def lemos(doc):
    zodziai = []
    for zodis in doc:
        if zodis.is_stop or zodis.is_punct or zodis.is_space:
            continue
        zodziai.append(zodis.lemma_.lower())
    return " ".join(zodziai)

def lematizuoti(tekstas):
    return lemos(nlp(tekstas))


# --- Pavardžių žodynas ---
# Pavardės imamos iš duomenų kalbėtojo sąrašo. Ieškoma pagal šaknį be galūnės, kad tiktų visi linksniai. 
# Pvz., "Skvernel" tiktų "Skvernelis", "Skvernelio", "Skvernelį" ir pan.

GALUNES =("as", "is", "ys", "us", "ė", "a")

def pavardes_saknis(pavarde):
    p = pavarde.lower()
    for galune in GALUNES:
        if p.endswith(galune):
            return p[:-len(galune)]
    return p


def pavardziu_zodynas(fragmentai):
    zodynas = {}
    for f in fragmentai:
        kalbetojas = f.get("kalbetojas")
        if not kalbetojas:
            continue
        pavarde = kalbetojas.split()[-1]
        for dalis in pavarde.split("-"):
            saknis = pavardes_saknis(dalis)
            zodynas.setdefault(saknis, set()).add(kalbetojas)
    return zodynas


PAVARDES = pavardziu_zodynas(nuskaityti_fragmentus())


def rasti_esybes(tekstas_lema):
    return []

def praturtinti(fragmentai):
    for fragmentas in fragmentai:
        fragmentas["tekstas_lema"] = lematizuoti(fragmentas["tekstas"])
        fragmentas["esybes"] = rasti_esybes(fragmentas["tekstas_lema"])
    return fragmentai

# --- Rakto ištraukimas iš frazės ---
# Raktas = kalbėtojas, frakcija, metai, mėnuo. Jis gali būti nepilnas: grąžinami tik tie laukai, kurie rasti frazėje. Pavyzdys:
# "Ką Skvernelis kalbėjo apie energetiką 2025 m. lapkritį?"

# Kamienas su "=" gale reiškia tikslų žodį (be galūnių), nes kitaip susipainiotų su kitais žodžiais:
#   "kovo=", "kovas=" (be "kovos", "kovą" - tai "kova", kaip kova su korupcija),
#   "liepos=", "liepa=" (ne "liep-", nes "liepia"), "spali-" (ne "spal-", nes "spalva").
MENESIU_KAMIENAI = {
    1: ("sausi",),
    2: ("vasaris=", "vasario", "vasarį"),    
    3: ("kovo=", "kovas="),
    4: ("baland",),
    5: ("geguž",),
    6: ("biržel",),
    7: ("liepos=", "liepa=", "liepą="),
    8: ("rugpjūt", "rugpjūč"),
    9: ("rugsėj",),
    10: ("spali", "spalį="),
    11: ("lapkri", "lapkrit"),
    12: ("gruod",),
}

def rasti_menesi(fraze):
    zodziai = re.findall(r"\w+", fraze.lower())
    for menuo, kamienai in MENESIU_KAMIENAI.items():
        for k in kamienai:
            if k.endswith("="):
                if k[:-1] in zodziai:
                    return menuo
            elif any(z.startswith(k) for z in zodziai):
                return menuo
    return None



def rasti_kalbetoja(fraze):
    zodziai = re.findall(r"\w+", fraze.lower())
    rasti = set()
    for saknis, kalbetojai in PAVARDES.items():
        if any(z.startswith(saknis) for z in zodziai):
            rasti = rasti | kalbetojai
    return sorted(rasti)



FRAKCIJU_KAMIENAI = {
    "LSDPF": ("socialdemokrat", "lsdp"),
    "TS-LKDF": ("konservator", "ts=", "lkd"),
    "NAF": ("aušr", "naf="),
    "LVŽ-KŠSF": ("valstieč", "lvž"),
    "LSF": ("liberal", "lsf="),
    "DFVL": ("demokratai=", "demokratų=", "demokratams=", "demokratus=", "vardan", "dfvl="),
    "MSNG": ("mišr", "msng="),
}



def rasti_frakcija(fraze):
    zodziai = re.findall(r"\w+", fraze.lower())
    rasti = set()
    for frakcija, kamienai in FRAKCIJU_KAMIENAI.items():
        for k in kamienai:
            if k.endswith("="):
                if k[:-1] in zodziai:
                    rasti.add(frakcija)
            elif any(z.startswith(k) for z in zodziai):
                rasti.add(frakcija)
    return sorted(rasti)


def istraukti_rakta(fraze):
    raktas = {}

    metai =re.search(r"\b(20\d{2})\b", fraze)
    if metai:
        raktas["metai"] = int(metai.group(1))

    menuo = rasti_menesi(fraze)
    if menuo:
        raktas["menuo"] = menuo
    
    kalbetojas = rasti_kalbetoja(fraze)
    if kalbetojas:
        raktas["kalbetojas"] = kalbetojas

    frakcija = rasti_frakcija(fraze)
    if frakcija:
        raktas["frakcija"] = frakcija
    return raktas
