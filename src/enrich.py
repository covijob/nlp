import random
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

NE_PAVARDES = {"kairė", "kairės", "kairę", "kairėje", "kairei",
    "kairieji", "kairiųjų", "kairiesiems", "kairiuosius",}

INSTITUCIJOS = {
    "Seimas": ("seim",),
    "Vyriausybė": ("vyriausyb",),
    "Prezidentas": ("prezident",),
    "Ministras Pirmininkas": ("ministr pirminink", "premjer"),
    "NATO": ("nato",),
    "ES": ("europ sąjung", "es="),
    "Europos Komisija": ("europ komisij",),
    "Europos Parlamentas": ("europ parlament",),
    "Rusija": ("rusij",),
    "Ukraina": ("ukrain",),
    "Baltarusija": ("baltarusij",),
    "JAV": ("jav=", "jungtin valstij"),
    "Kinija": ("kinij",),
    "Konstitucinis Teismas": ("konstitucin teism",),
    "Lietuvos bankas": ("lietuv bank",),
    "Valstybės kontrolė": ("valstyb kontrol",),
    "Savivaldybės": ("savivaldyb",),
    "Prokuratūra": ("prokurat",),
    "STT": ("stt=", "specialiųj tyrim tarnyb"),
    "VSD": ("vsd=", "valstyb saugum departament"),
    "Sodra": ("sodr",),
    "VMI": ("vmi=", "mokest inspekcij"),
    "Kariuomenė": ("kariuomen",),
    "Policija": ("policij",),
    "Finansų ministerija": ("finans minist",),
    "Sveikatos apsaugos ministerija": ("sveikat apsaug minist",),
    "Švietimo, mokslo ir sporto ministerija": ("švietim moksl sport minist",),
    "Krašto apsaugos ministerija": ("krašt apsaug minist",),
    "Užsienio reikalų ministerija": ("užsieni reikal minist",),
    "Vidaus reikalų ministerija": ("vidaus reikal minist",),
    "Socialinės apsaugos ir darbo ministerija": ("socialin apsaug darb minist",),
    "Teisingumo ministerija": ("teisingum minist",),
    "Energetikos ministerija": ("energetik minist",),
    "Ekonomikos ir inovacijų ministerija": ("ekonomik inovacij minist",),
    "Susisiekimo ministerija": ("susisiekim minist",),
    "Žemės ūkio ministerija": ("žem ūk minist",),
    "Aplinkos ministerija": ("aplink minist",),
    "Kultūros ministerija": ("kultūr minist",),
}

def rasti_esybes(tekstas_lema):
    rasta = set()
    for pavadinimas, formos in INSTITUCIJOS.items():
        for forma in formos:
            dalys = []
            for zodis in forma.split():
                if zodis.endswith("="):
                    dalys.append(re.escape(zodis[:-1]) + r"\b")
                else:
                    dalys.append(re.escape(zodis) + r"\w*")
            if re.search(r"\b" + r"\s+".join(dalys), tekstas_lema):
                rasta.add(pavadinimas)
    rasta = rasta | set(rasti_kalbetoja(tekstas_lema))
    return sorted(rasta)

def praturtinti(fragmentai):
    tekstai = []
    for f in fragmentai:
        tekstai.append(f["tekstas"])

    dokumentai = list(nlp.pipe(tekstai, batch_size=50))

    for i in range(len(fragmentai)):
        fragmentai[i]["tekstas_lema"] = lemos(dokumentai[i])
        fragmentai[i]["esybes"] = rasti_esybes(fragmentai[i]["tekstas_lema"])
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
    for z in zodziai:
        if z in NE_PAVARDES:
            continue
        geriausia = None
        for saknis in PAVARDES:
            if z.startswith(saknis):
                if geriausia is None or len(saknis) > len(geriausia):
                    geriausia = saknis
        if geriausia:
            rasti = rasti | PAVARDES[geriausia]
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
