from django.urls import path

from paieska import views

urlpatterns = [
    path("", views.frazes, name="frazes"),
    path("tyrimas/", views.tyrimas, name="tyrimas"),
    path("rezultatai/", views.rezultatai_sarasas, name="rezultatai_sarasas"),
    path("rezultatai/<int:tyrimo_id>/", views.rezultatai, name="rezultatai"),
]
