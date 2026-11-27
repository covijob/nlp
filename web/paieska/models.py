from django.db import models

METODAI = [("bge", "Tik BGE-M3"), ("raktas_bge", "Raktas + BGE-M3")]
IRENGINIAI = [("cpu", "CPU"), ("cuda", "GPU")]


class Fraze(models.Model):
    tekstas = models.CharField(max_length=500, unique=True)
    sukurta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.tekstas


class Tyrimas(models.Model):
    frazes = models.ManyToManyField(Fraze)
    metodas = models.CharField(max_length=20, choices=METODAI)
    irenginys = models.CharField(max_length=10, choices=IRENGINIAI)
    rezultatai = models.JSONField(default=list)
    trukme = models.FloatField(default=0)
    sukurta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
