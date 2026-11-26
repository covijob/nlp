import random
import numpy as np
from duomenys import BGE_M3

METODAI = ["bge", "raktas_bge"]


def ikelti_modeli(irenginys="cpu"):
    """Įkelia BGE-M3 iš models/bge-m3. irenginys: "cpu" arba "cuda"."""
    from FlagEmbedding import BGEM3FlagModel

    fp16 = irenginys == "cuda"
    try:
        return BGEM3FlagModel(str(BGE_M3), use_fp16=fp16, devices=irenginys)
    except TypeError:  
        return BGEM3FlagModel(str(BGE_M3), use_fp16=fp16, device=irenginys)


def skaiciuoti_vektorius(tekstai, modelis):
    # BGE-M3 kiekvieną tekstą paverčia vektoriumi; ilgesni nei 512 teksto vienetų tekstai apkarpomi
    vektoriai = modelis.encode(tekstai, batch_size=16, max_length=512)["dense_vecs"]
    return np.asarray(vektoriai, dtype="float32")


def filtruoti(fragmentai, raktas, be_triuksmo=True):
    raise NotImplementedError


def _normalizuoti(m):
    """Normalizuojame, kad skaliarinė sandauga būtų kosinuso panašumas."""
    m = np.asarray(m, dtype="float32")
    # kiekvieną vektorių padalijame iš jo ilgio, tada visų ilgis lygus 1
    # clip(min=1e-12) apsaugo nuo dalybos iš nulio, jei vektorius būtų nulinis
    return m / np.linalg.norm(m, axis=-1, keepdims=True).clip(min=1e-12)


def ieskoti(fraze, metodas, k, fragmentai, vektoriai=None, modelis=None):
    if metodas not in METODAI:
        raise ValueError(metodas)

    if metodas == "raktas_bge":
        # hibridinė paieška dar nepadaryta: laikinas pakaitalas
        return random.sample(fragmentai, min(k, len(fragmentai)))

    # metodas == "bge": paprasta vektorinė paieška tarp visų fragmentų
    if vektoriai is None or modelis is None:
        raise ValueError("Metodui 'bge' reikia nurodyti vektorius ir modelį")
    if len(vektoriai) != len(fragmentai):
        raise ValueError(
            f"Vektorių ({len(vektoriai)}) ir fragmentų ({len(fragmentai)}) skaičius nesutampa"
        )
    # frazę paverčiame vektoriumi tuo pačiu modeliu kaip ir fragmentus
    q = _normalizuoti(skaiciuoti_vektorius([fraze], modelis))[0]
    # visų fragmentų vektoriai x frazės vektorius = panašumo balas kiekvienam fragmentui
    balai = _normalizuoti(vektoriai) @ q
    # rikiuojame nuo didžiausio balo ir paimame k geriausių indeksų
    top = np.argsort(-balai)[:k]
    # grąžiname fragmentus (visus jų laukus) kartu su balu
    return [{**fragmentai[i], "balas": float(balai[i])} for i in top]
