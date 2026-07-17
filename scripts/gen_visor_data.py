#!/usr/bin/env python3
"""Genera JS con datos reales del JSON extraido para el visor"""
import json, sys, os
from pathlib import Path

BASE = Path("/root/workspace/ERAVisor")

def gen_visor_js(paises=None):
    if not paises:
        paises = ["es"]
    
    todos = []
    for p in paises:
        f = BASE / "data" / f"{p}_extraido.json"
        if f.exists():
            with open(f) as fh:
                data = json.load(fh)
                for r in data:
                    r.setdefault("pais", p.upper())
                    # Asegurar coordenadas aproximadas
                    if "provincia" in r and r["provincia"] and "latitud" not in r:
                        coord_lookup = {
                            "Madrid": (40.4168, -3.7038), "Barcelona": (41.3874, 2.1686),
                            "Valencia": (39.4699, -0.3763), "Sevilla": (37.3891, -5.9845),
                            "Bilbao": (43.2630, -2.9350), "Málaga": (36.7213, -4.4214),
                            "Vigo": (42.2406, -8.7207), "Oviedo": (43.3619, -5.8494),
                            "Zaragoza": (41.6488, -0.8891), "Alicante": (38.3452, -0.4810),
                            "Murcia": (37.9922, -1.1307), "Granada": (37.1773, -3.5986),
                            "Toledo": (39.8628, -4.0273), "Burgos": (42.3440, -3.6969),
                            "León": (42.5987, -5.5671), "Pontevedra": (42.4307, -8.6444),
                            "A Coruña": (43.3623, -8.4115), "Tarragona": (41.1189, 1.2445),
                            "Girona": (41.9794, 2.8214), "Lleida": (41.6176, 0.6200),
                            "Cádiz": (36.5298, -6.2928), "Almería": (36.8381, -2.4597),
                            "Huelva": (37.2614, -6.9447), "Castellón": (39.9864, -0.0513),
                            "Salamanca": (40.9701, -5.6635), "Valladolid": (41.6523, -4.7245),
                            "Guipúzcoa": (43.3126, -1.9756), "Vizcaya": (43.2630, -2.9350),
                            "Álava": (42.8500, -2.6800), "Palencia": (42.0096, -4.5314),
                        }
                        for k, v in coord_lookup.items():
                            if k.lower() in r["provincia"].lower():
                                r["latitud"] = v[0]
                                r["longitud"] = v[1]
                                break
                    if "latitud" not in r:
                        r["latitud"] = 40.0
                        r["longitud"] = -3.0
                    if "fallecidos" not in r:
                        r["fallecidos"] = 0
                    if "heridos_graves" not in r:
                        r["heridos_graves"] = 0
                    if "suceso_codigo" not in r:
                        r["suceso_codigo"] = "1.7"
                    if "causa_codigo" not in r:
                        r["causa_codigo"] = "2.4"
                todos.extend(data)
    
    return todos

def main():
    resultados = gen_visor_js(["es"])
    output = f"window.DATOS = {json.dumps(resultados, ensure_ascii=False, indent=2)};\n"
    visor_dir = BASE / "visor"
    visor_dir.mkdir(parents=True, exist_ok=True)
    
    with open(visor_dir / "datos.js", "w", encoding="utf-8") as f:
        f.write(output)
    
    # También copiar datos de ejemplo al index.html (reemplazar window.DATOS)
    idx_file = visor_dir / "index.html"
    if idx_file.exists():
        with open(idx_file) as f:
            html = f.read()
        # Buscar y reemplazar datos de ejemplo
        import re
        # Si hay window.DATOS en línea, lo reemplazamos con los datos reales
        if "window.DATOS" in html:
            # Es mejor añadir un script tag que cargue datos.js
            if '<script src="datos.js"></script>' not in html:
                html = html.replace("<script>", '<script src="datos.js"></script>\n<script>')
                with open(idx_file, "w") as f:
                    f.write(html)
                print("✅ datos.js injectado en index.html")
    
    print(f"📊 {len(resultados)} accidentes procesados para visor")

if __name__ == "__main__":
    main()