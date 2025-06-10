import requests
from django.core.management.base import BaseCommand
from apps.alquiler.models import Provincia, Departamento, Localidad

GEORREF_BASE = "https://apis.datos.gob.ar/georef/api"

class Command(BaseCommand):
    help = "Carga provincias, departamentos y localidades desde la API de Georef"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Cargando provincias..."))
        resp = requests.get(f"{GEORREF_BASE}/provincias", params={"campos": "nombre", "max": 100})
        provincias = resp.json().get("provincias", [])

        for p in provincias:
            nombre_prov = p["nombre"]
            provincia, _ = Provincia.objects.get_or_create(nombre=nombre_prov)
            self.stdout.write(f" - {provincia.nombre}")

            # Departamentos
            self.stdout.write(f"   Cargando departamentos para {nombre_prov}...")
            deps_resp = requests.get(f"{GEORREF_BASE}/departamentos", params={"provincia": nombre_prov, "campos": "nombre", "max": 500})
            departamentos = deps_resp.json().get("departamentos", [])
            for d in departamentos:
                nombre_dep = d["nombre"]
                depto, _ = Departamento.objects.get_or_create(nombre=nombre_dep, provincia=provincia)

                # Localidades
                self.stdout.write(f"     Cargando localidades para {nombre_dep}...")
                locs_resp = requests.get(f"{GEORREF_BASE}/localidades", params={
                    "provincia": nombre_prov,
                    "departamento": nombre_dep,
                    "campos": "nombre",
                    "max": 1000
                })
                localidades = locs_resp.json().get("localidades", [])
                for l in localidades:
                    nombre_loc = l["nombre"]
                    Localidad.objects.get_or_create(nombre=nombre_loc, departamento=depto)

        self.stdout.write(self.style.SUCCESS("¡Carga de datos completa!"))


