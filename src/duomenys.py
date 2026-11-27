import json
from pathlib import Path

import numpy as np

SAKNIS = Path(__file__).resolve().parent.parent
DATA = SAKNIS / "data"
MODELIAI = SAKNIS / "models"
EVAL = SAKNIS / "eval"

FRAGMENTAI = DATA / "fragmentai.jsonl"
FRAGMENTAI_SAMPLE = DATA / "fragmentai_sample.jsonl"
VEKTORIAI = DATA / "vektoriai.npy"
VEKTORIAI_SAMPLE = DATA / "vektoriai_sample.npy"
BGE_M3 = MODELIAI / "bge-m3"

LAUKAI = [
    "id",
    "data",
    "posedis",
    "kalbetojas",
    "frakcija",
    "tekstas",
    "tekstas_lema",
    "esybes",
    "triuksmas",
]


def naujas_fragmentas(id, data, posedis, kalbetojas, frakcija, tekstas):
    return {
        "id": id,
        "data": data,
        "posedis": posedis,
        "kalbetojas": kalbetojas,
        "frakcija": frakcija,
        "tekstas": tekstas,
        "tekstas_lema": tekstas.lower(),
        "esybes": [],
        "triuksmas": False,
    }


def nuskaityti_jsonl(kelias):
    with open(kelias, encoding="utf-8") as f:
        return [json.loads(eilute) for eilute in f if eilute.strip()]


def issaugoti_jsonl(irasai, kelias):
    Path(kelias).parent.mkdir(parents=True, exist_ok=True)
    with open(kelias, "w", encoding="utf-8") as f:
        for irasas in irasai:
            f.write(json.dumps(irasas, ensure_ascii=False) + "\n")


def nuskaityti_fragmentus(kelias=None):
    if kelias is None:
        kelias = FRAGMENTAI if FRAGMENTAI.exists() else FRAGMENTAI_SAMPLE
    return nuskaityti_jsonl(kelias)


def issaugoti_fragmentus(fragmentai, kelias=FRAGMENTAI):
    issaugoti_jsonl(fragmentai, kelias)


def nuskaityti_vektorius(kelias=VEKTORIAI):
    return np.load(kelias)


def issaugoti_vektorius(vektoriai, kelias=VEKTORIAI):
    np.save(kelias, vektoriai)
