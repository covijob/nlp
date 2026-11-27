import argparse
import math
import re
from collections import Counter

import pdfplumber

from duomenys import DATA, FRAGMENTAI, FRAGMENTAI_SAMPLE, issaugoti_fragmentus, naujas_fragmentas

MAX_ZODZIU = 300
SAMPLE_DYDIS = 500

MENESIAI = {
    "sausio": 1,
    "vasario": 2,
    "kovo": 3,
    "balandžio": 4,
    "gegužės": 5,
    "birželio": 6,
    "liepos": 7,
    "rugpjūčio": 8,
    "rugsėjo": 9,
    "spalio": 10,
    "lapkričio": 11,
    "gruodžio": 12,
}

DATA_RE = re.compile(r"^(\d{4}) m\. (\w+) (\d{1,2})(?:\s*–\s*\d{1,2})? d\.$")
POSEDIS_RE = re.compile(r"(\w+) POSĖDŽIO NR\. (\d+)")
ETIKETE_RE = re.compile(r"^(?P<vardas>[^()]+?)\s*(?:\((?P<skliaustai>[^()]*)\))?\s*\.?$")
SAKINIO_RIBA = re.compile(r"(?<=[.!?…])\s+")
POSEDZIU_TIPAI = {
    "RYTINIO": "rytinis",
    "VAKARINIO": "vakarinis",
    "NENUMATYTO": "nenumatytas",
    "NEEILINIO": "neeilinis",
}
PIRMININKAI = {"PIRMININKAS", "PIRMININKĖ"}
SKYRYBA = set(" .,()–-\xa0")


def yra_bold(c):
    return "Bold" in c["fontname"]


def yra_italic(c):
    return "Italic" in c["fontname"]


def zymos_tarpai(simboliai):
    zymos = set()
    for i in range(len(simboliai) - 1):
        c, kitas = simboliai[i], simboliai[i + 1]
        if c["text"].isspace() and abs(kitas["top"] - c["top"]) < 1 and kitas["x0"] < c["x1"] - 0.5:
            zymos.add(id(c))
    return zymos


def isvalytas_puslapis(puslapis):
    zymos = zymos_tarpai(puslapis.chars)
    return puslapis.filter(
        lambda o: o.get("object_type") != "char" or (id(o) not in zymos and o["size"] >= 7)
    )


def surinkti(simboliai):
    dalys = []
    ankstesnis = None
    for c in simboliai:
        if ankstesnis is not None and c["x0"] - ankstesnis["x1"] > 1:
            dalys.append(" ")
        dalys.append(c["text"])
        ankstesnis = c
    return re.sub(r"\s+", " ", "".join(dalys)).strip()


def eilutes_tipas(simboliai):
    raides = [c for c in simboliai if not c["text"].isspace()]
    if not raides:
        return None
    bold = [c for c in raides if yra_bold(c)]
    italic = [c for c in raides if yra_italic(c) and not yra_bold(c)]
    if len(bold) > len(raides) / 2:
        if raides[0]["size"] >= 11:
            return "antraste"
        if raides[0]["size"] >= 10:
            return "darbotvarke"
    if len(italic) == len(raides):
        return "pastaba"
    return "tekstas"


def etiketes_simbolis(c):
    return c["size"] < 10 and (yra_bold(c) or yra_italic(c))


def atskirti_etikete(simboliai):
    raides = [c for c in simboliai if not c["text"].isspace()]
    if not raides or not etiketes_simbolis(raides[0]):
        return None, simboliai
    riba = 0
    for i, c in enumerate(simboliai):
        if etiketes_simbolis(c):
            riba = i + 1
        elif c["text"] not in SKYRYBA:
            break
    while riba < len(simboliai) and simboliai[riba]["text"].isspace():
        riba += 1
    if riba < len(simboliai) and simboliai[riba]["text"] == "(" and riba + 1 < len(simboliai) and yra_italic(simboliai[riba + 1]):
        riba += 1
    if neuzbaigta(surinkti(simboliai[:riba])):
        uzdarymas = next((i for i in range(riba, len(simboliai)) if simboliai[i]["text"] == ")"), None)
        if uzdarymas is not None:
            riba = uzdarymas + 1
    while riba < len(simboliai) and simboliai[riba]["text"] in ").":
        riba += 1
    return surinkti(simboliai[:riba]), simboliai[riba:]


def be_pastabu(simboliai):
    return [c for c in simboliai if not (yra_italic(c) and c["size"] >= 10)]


def istraukti_teksta(pdf_kelias):
    eilutes = []
    with pdfplumber.open(pdf_kelias) as pdf:
        for puslapis in pdf.pages:
            for eilute in isvalytas_puslapis(puslapis).extract_text_lines(return_chars=True):
                simboliai = eilute["chars"]
                tipas = eilutes_tipas(simboliai)
                if tipas is None:
                    continue
                if tipas != "tekstas":
                    eilutes.append({"tipas": tipas, "tekstas": surinkti(simboliai)})
                    continue
                etikete, likusi = atskirti_etikete(simboliai)
                tekstas = surinkti(be_pastabu(likusi))
                if etikete:
                    tekstas = tekstas.lstrip(".,: ")
                eilutes.append({"tipas": "tekstas", "etikete": etikete, "tekstas": tekstas})
    return eilutes


def sujungti_eilutes(eilutes):
    tekstas = ""
    for eilute in eilutes:
        if not eilute:
            continue
        if tekstas.endswith("-") and len(tekstas) > 1 and tekstas[-2].isalpha():
            tekstas = tekstas[:-1] + eilute if eilute[0].islower() else tekstas + eilute
        else:
            tekstas = f"{tekstas} {eilute}" if tekstas else eilute
    return tekstas


def isvalyti(tekstas):
    tekstas = re.sub(r"\(\s*\)", " ", tekstas)
    tekstas = re.sub(r"\s+([.,;:?!…])", r"\1", tekstas)
    tekstas = re.sub(r"\s+", " ", tekstas)
    return tekstas.strip()


def gauti_data(eilute):
    m = DATA_RE.match(eilute)
    if not m or m.group(2) not in MENESIAI:
        return None
    return f"{int(m.group(1)):04d}-{MENESIAI[m.group(2)]:02d}-{int(m.group(3)):02d}"


def gauti_posedi(eilute):
    m = POSEDIS_RE.search(eilute)
    if m:
        return f"{POSEDZIU_TIPAI.get(m.group(1), m.group(1).lower())} Nr. {m.group(2)}"
    if "MINĖJIM" in eilute:
        return "iškilmingas minėjimas"
    return None


def vardas(tekstas):
    return tekstas.strip().title()


def neuzbaigta(etikete):
    return etikete.count("(") > etikete.count(")")


def kalbetojas_ir_frakcija(etikete, pirmininkai):
    m = ETIKETE_RE.match(etikete)
    if not m:
        return vardas(etikete), None
    pavadinimas = m.group("vardas").strip().rstrip(".").strip()
    skliaustai = m.group("skliaustai")
    if pavadinimas in PIRMININKAI:
        if skliaustai:
            dalys = [d.strip() for d in skliaustai.split(",", 1)]
            pirmininkai[pavadinimas] = (vardas(dalys[0]), dalys[1] if len(dalys) > 1 else None)
        return pirmininkai.get(pavadinimas, (vardas(pavadinimas), None))
    return vardas(pavadinimas), skliaustai.strip() if skliaustai else None


def skaidyti(eilutes):
    fragmentai = []
    data = posedis = None
    pirmininkai = {}
    dabartinis = None

    def uzdaryti():
        nonlocal dabartinis
        if dabartinis is not None:
            tekstas = isvalyti(sujungti_eilutes(dabartinis["eilutes"]))
            if tekstas:
                fragmentai.append(
                    naujas_fragmentas(
                        len(fragmentai),
                        dabartinis["data"],
                        dabartinis["posedis"],
                        dabartinis["kalbetojas"],
                        dabartinis["frakcija"],
                        tekstas,
                    )
                )
        dabartinis = None

    for eilute in eilutes:
        tipas = eilute["tipas"]
        if tipas == "antraste":
            if "RODYKLĖ" in eilute["tekstas"]:
                uzdaryti()
                break
            naujas_posedis = gauti_posedi(eilute["tekstas"])
            if naujas_posedis:
                uzdaryti()
                posedis, data, pirmininkai = naujas_posedis, None, {}
            data = gauti_data(eilute["tekstas"]) or data
            continue
        if tipas != "tekstas" or posedis is None:
            continue
        etikete = eilute["etikete"]
        if etikete and dabartinis is not None and neuzbaigta(dabartinis["etikete"]) and not dabartinis["eilutes"]:
            etikete = f"{dabartinis['etikete']} {etikete}"
            dabartinis = None
        if etikete:
            uzdaryti()
            kalbetojas, frakcija = kalbetojas_ir_frakcija(etikete, pirmininkai)
            dabartinis = {
                "data": data,
                "posedis": posedis,
                "etikete": etikete,
                "kalbetojas": kalbetojas,
                "frakcija": frakcija,
                "eilutes": [],
            }
        if dabartinis is not None and eilute["tekstas"]:
            dabartinis["eilutes"].append(eilute["tekstas"])
    uzdaryti()
    return fragmentai


def sakiniai(tekstas):
    return [s for s in SAKINIO_RIBA.split(tekstas) if s]


def dalys_po_zodziu(zodziai, max_zodziu):
    return [" ".join(zodziai[i : i + max_zodziu]) for i in range(0, len(zodziai), max_zodziu)]


def perkirpti(fragmentas, max_zodziu=MAX_ZODZIU):
    viso = len(fragmentas["tekstas"].split())
    if viso <= max_zodziu:
        return [fragmentas]
    tikslas = viso / math.ceil(viso / max_zodziu)
    dalys = []
    dabartine = []
    ilgis = 0
    for sakinys in sakiniai(fragmentas["tekstas"]):
        zodziai = sakinys.split()
        if dabartine and (ilgis + len(zodziai) > max_zodziu or ilgis >= tikslas):
            dalys.append(" ".join(dabartine))
            dabartine, ilgis = [], 0
        if len(zodziai) > max_zodziu:
            dalys.extend(dalys_po_zodziu(zodziai, max_zodziu))
            continue
        dabartine.append(sakinys)
        ilgis += len(zodziai)
    if dabartine:
        dalys.append(" ".join(dabartine))
    return [{**fragmentas, "tekstas": dalis, "tekstas_lema": dalis.lower()} for dalis in dalys]


def uzpildyti_frakcijas(fragmentai):
    zinomos = {}
    for f in fragmentai:
        if f["frakcija"]:
            zinomos.setdefault(f["kalbetojas"], Counter())[f["frakcija"]] += 1
    for f in fragmentai:
        if not f["frakcija"] and f["kalbetojas"] in zinomos:
            f["frakcija"] = zinomos[f["kalbetojas"]].most_common(1)[0][0]
    return fragmentai


def apdoroti(pdf_keliai):
    fragmentai = []
    for kelias in pdf_keliai:
        for fragmentas in skaidyti(istraukti_teksta(kelias)):
            fragmentai.extend(perkirpti(fragmentas))
    uzpildyti_frakcijas(fragmentai)
    for i, fragmentas in enumerate(fragmentai):
        fragmentas["id"] = i
    return fragmentai


def pavyzdys(fragmentai, dydis=SAMPLE_DYDIS):
    atrinkti = []
    for posedis in dict.fromkeys(f["posedis"] for f in fragmentai):
        if len(atrinkti) >= dydis:
            break
        atrinkti.extend(f for f in fragmentai if f["posedis"] == posedis)
    return atrinkti


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()
    pdf_keliai = sorted(DATA.glob("*.pdf"))
    if args.sample:
        issaugoti_fragmentus(pavyzdys(skaidyti(istraukti_teksta(pdf_keliai[0]))), FRAGMENTAI_SAMPLE)
    else:
        issaugoti_fragmentus(apdoroti(pdf_keliai), FRAGMENTAI)
