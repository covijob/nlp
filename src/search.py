import random

from duomenys import BGE_M3

METODAI = ["bge", "raktas_bge"]


def ikelti_modeli(irenginys="cpu"):
    raise NotImplementedError


def skaiciuoti_vektorius(tekstai, modelis):
    raise NotImplementedError


def filtruoti(fragmentai, raktas, be_triuksmo=True):
    raise NotImplementedError


def ieskoti(fraze, metodas, k, fragmentai, vektoriai=None, modelis=None):
    if metodas not in METODAI:
        raise ValueError(metodas)
    return random.sample(fragmentai, min(k, len(fragmentai)))
