from django.shortcuts import get_object_or_404, redirect, render

from duomenys import EVAL, nuskaityti_jsonl

from . import grafikai, paslauga
from .models import METODAI, Fraze, Tyrimas

FRAZES_FAILAS = EVAL / "frazes.jsonl"


def ikelti_numatytas_frazes():
    if not FRAZES_FAILAS.exists():
        return
    for irasas in nuskaityti_jsonl(FRAZES_FAILAS):
        Fraze.objects.get_or_create(tekstas=irasas["tekstas"])


def frazes(request):
    klaida = None
    if request.method == "POST":
        tekstas = request.POST.get("tekstas", "").strip()
        if tekstas:
            Fraze.objects.get_or_create(tekstas=tekstas)
            return redirect("frazes")
        klaida = "Įrašyk frazę."
    ikelti_numatytas_frazes()
    return render(request, "paieska/frazes.html", {"frazes": Fraze.objects.all(), "klaida": klaida})


def tyrimas(request):
    irenginiai = [("cpu", "CPU")]
    if paslauga.gpu_yra():
        irenginiai.append(("cuda", "GPU"))
    klaida = None
    if request.method == "POST":
        pasirinktos = list(Fraze.objects.filter(id__in=request.POST.getlist("frazes")))
        metodas = request.POST.get("metodas")
        irenginys = request.POST.get("irenginys")
        if not pasirinktos:
            klaida = "Pažymėk bent vieną frazę."
        elif metodas not in dict(METODAI) or irenginys not in dict(irenginiai):
            klaida = "Neteisingas metodas arba įrenginys."
        else:
            rezultatai, trukme = paslauga.vykdyti([f.tekstas for f in pasirinktos], metodas, irenginys)
            naujas = Tyrimas.objects.create(
                metodas=metodas, irenginys=irenginys, rezultatai=rezultatai, trukme=trukme
            )
            naujas.frazes.set(pasirinktos)
            return redirect("rezultatai", tyrimo_id=naujas.id)
    return render(
        request,
        "paieska/tyrimas.html",
        {"frazes": Fraze.objects.all(), "metodai": METODAI, "irenginiai": irenginiai, "klaida": klaida},
    )


def rezultatai_sarasas(request):
    return render(request, "paieska/rezultatai_sarasas.html", {"tyrimai": Tyrimas.objects.all()})


def rezultatai(request, tyrimo_id):
    tyrimas = get_object_or_404(Tyrimas, id=tyrimo_id)
    frazes_rezultatai = [{**r, "grafikai": grafikai.grafikai(r)} for r in tyrimas.rezultatai]
    return render(request, "paieska/rezultatai.html", {"tyrimas": tyrimas, "frazes_rezultatai": frazes_rezultatai})
