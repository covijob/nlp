def lematizuoti(tekstas):
    return tekstas.lower()


def rasti_esybes(tekstas_lema):
    return []


def praturtinti(fragmentai):
    for fragmentas in fragmentai:
        fragmentas["tekstas_lema"] = lematizuoti(fragmentas["tekstas"])
        fragmentas["esybes"] = rasti_esybes(fragmentas["tekstas_lema"])
    return fragmentai


def istraukti_rakta(fraze):
    return {}
