from duomenys import DATA, FRAGMENTAI, issaugoti_fragmentus

MAX_ZODZIU = 300


def istraukti_teksta(pdf_kelias):
    raise NotImplementedError


def isvalyti(tekstas):
    raise NotImplementedError


def skaidyti(tekstas):
    raise NotImplementedError


def perkirpti(fragmentas, max_zodziu=MAX_ZODZIU):
    raise NotImplementedError


def uzpildyti_frakcijas(fragmentai):
    raise NotImplementedError


def apdoroti(pdf_keliai):
    raise NotImplementedError


if __name__ == "__main__":
    fragmentai = apdoroti(sorted(DATA.glob("*.pdf")))
    issaugoti_fragmentus(fragmentai, FRAGMENTAI)
