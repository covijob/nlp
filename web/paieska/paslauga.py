import random
import time
from collections import Counter

import numpy as np

import search
from duomenys import FRAGMENTAI, FRAGMENTAI_SAMPLE, VEKTORIAI, VEKTORIAI_SAMPLE, nuskaityti_fragmentus

K = 5
GRAFIKO_K = 50
ISTRAUKOS_ILGIS = 400

_fragmentai = None
_vektoriai = None
_modeliai = {}


def gpu_yra():
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def duomenys():
    global _fragmentai, _vektoriai
    if _fragmentai is None:
        if FRAGMENTAI.exists() and VEKTORIAI.exists():
            fragmentu_kelias, vektoriu_kelias = FRAGMENTAI, VEKTORIAI
        elif VEKTORIAI_SAMPLE.exists() or not FRAGMENTAI.exists():
            fragmentu_kelias, vektoriu_kelias = FRAGMENTAI_SAMPLE, VEKTORIAI_SAMPLE
        else:
            fragmentu_kelias, vektoriu_kelias = FRAGMENTAI, VEKTORIAI
        _fragmentai = nuskaityti_fragmentus(fragmentu_kelias)
        if vektoriu_kelias.exists():
            _vektoriai = np.load(vektoriu_kelias)
    return _fragmentai, _vektoriai


def modelis(irenginys):
    if irenginys not in _modeliai:
        try:
            _modeliai[irenginys] = search.ikelti_modeli(irenginys)
        except ImportError:
            _modeliai[irenginys] = None
    return _modeliai[irenginys]


def ieskoti_frazes(fraze, metodas, irenginys):
    fragmentai, vektoriai = duomenys()
    pastaba = None
    if metodas == "bge":
        m = modelis(irenginys) if vektoriai is not None else None
        if vektoriai is None or m is None:
            pastaba = "Nėra vektorių arba modelio, rodomi atsitiktiniai fragmentai."
            rasti = random.sample(fragmentai, min(GRAFIKO_K, len(fragmentai)))
        else:
            rasti = search.ieskoti(fraze, metodas, GRAFIKO_K, fragmentai, vektoriai, m)
    else:
        rasti = search.ieskoti(fraze, metodas, GRAFIKO_K, fragmentai)
    return rasti, pastaba


def vykdyti(frazes, metodas, irenginys):
    rezultatai = []
    pradzia = time.perf_counter()
    for fraze in frazes:
        frazes_pradzia = time.perf_counter()
        rasti, pastaba = ieskoti_frazes(fraze, metodas, irenginys)
        rezultatai.append(
            {
                "fraze": fraze,
                "trukme": round(time.perf_counter() - frazes_pradzia, 3),
                "pastaba": pastaba,
                "menesiai": dict(Counter(f["data"][:7] for f in rasti if f["data"])),
                "frakcijos": dict(Counter(f["frakcija"] or "Be frakcijos" for f in rasti)),
                "fragmentai": [
                    {
                        "id": f["id"],
                        "kalbetojas": f["kalbetojas"],
                        "frakcija": f["frakcija"],
                        "data": f["data"],
                        "istrauka": f["tekstas"][:ISTRAUKOS_ILGIS],
                        "balas": f.get("balas"),
                    }
                    for f in rasti[:K]
                ],
            }
        )
    return rezultatai, round(time.perf_counter() - pradzia, 3)
