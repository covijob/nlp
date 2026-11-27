import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SPALVA = "#257de0"
TEKSTAS = "#191919"
TEKSTAS_ANTRINIS = "#666666"
TINKLELIS = "#e5e5e5"
STULPELIO_PLOTIS = 0.5
MAZIAUSIAI_STULPELIU = 6

MENESIAI = ["sau", "vas", "kov", "bal", "geg", "bir", "lie", "rgp", "rgs", "spa", "lap", "gru"]


def menesio_pavadinimas(raktas):
    metai, menuo = raktas.split("-")
    return f"{metai} {MENESIAI[int(menuo) - 1]}"


def visi_menesiai(nuo, iki):
    metai, menuo = map(int, nuo.split("-"))
    raktai = []
    while f"{metai:04d}-{menuo:02d}" <= iki:
        raktai.append(f"{metai:04d}-{menuo:02d}")
        metai, menuo = (metai + 1, 1) if menuo == 12 else (metai, menuo + 1)
    return raktai


def paruosti_asis(ax, pavadinimas):
    ax.set_title(pavadinimas, loc="left", color=TEKSTAS, fontsize=10, pad=10)
    for puse in ("top", "right", "left"):
        ax.spines[puse].set_visible(False)
    ax.spines["bottom"].set_color(TINKLELIS)
    ax.tick_params(colors=TEKSTAS_ANTRINIS, labelsize=8, length=0)


def paveiksliukas(fig):
    buferis = io.BytesIO()
    fig.savefig(buferis, format="png", dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return base64.b64encode(buferis.getvalue()).decode("ascii")


def menesiu_grafikas(menesiai):
    raktai = visi_menesiai(min(menesiai), max(menesiai))
    reiksmes = [menesiai.get(r, 0) for r in raktai]
    fig, ax = plt.subplots(figsize=(4.2, 2.6))
    paruosti_asis(ax, "Paminėjimai per mėnesius")
    ax.bar(range(len(raktai)), reiksmes, width=STULPELIO_PLOTIS, color=SPALVA)
    ax.set_xticks(range(len(raktai)), [menesio_pavadinimas(r) for r in raktai])
    ax.set_yticks([])
    for i, v in enumerate(reiksmes):
        ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8, color=TEKSTAS)
    ax.set_ylim(0, max(reiksmes) * 1.2)
    tarpas = max(0.6, (MAZIAUSIAI_STULPELIU - len(raktai)) / 2)
    ax.set_xlim(-tarpas, len(raktai) - 1 + tarpas)
    return paveiksliukas(fig)


def frakciju_grafikas(frakcijos):
    poros = sorted(frakcijos.items(), key=lambda p: p[1])
    pavadinimai = [p[0] for p in poros]
    reiksmes = [p[1] for p in poros]
    fig, ax = plt.subplots(figsize=(4.2, 0.35 * len(poros) + 0.9))
    paruosti_asis(ax, "Paminėjimai pagal frakcijas")
    ax.barh(range(len(poros)), reiksmes, height=STULPELIO_PLOTIS, color=SPALVA)
    ax.set_yticks(range(len(poros)), pavadinimai)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(TINKLELIS)
    for i, v in enumerate(reiksmes):
        ax.text(v, i, f" {v}", ha="left", va="center", fontsize=8, color=TEKSTAS)
    ax.set_xlim(0, max(reiksmes) * 1.2)
    return paveiksliukas(fig)


def grafikai(rezultatas):
    menesiai = rezultatas.get("menesiai") or {}
    frakcijos = rezultatas.get("frakcijos") or {}
    return {
        "menesiai": menesiu_grafikas(menesiai) if menesiai else None,
        "frakcijos": frakciju_grafikas(frakcijos) if frakcijos else None,
    }
