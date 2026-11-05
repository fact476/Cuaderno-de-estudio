#!/usr/bin/env python3
"""Genera catalogo.json a partir de rutas.json y de los tutoriales que existen.

Cada tutorial es un .html dentro de la carpeta de su ruta (por ejemplo
futuros/micro-e-mini.html) y se describe a sí mismo con etiquetas en <head>:

    <title>Micro E-mini S&P 500</title>
    <meta name="description" content="Qué vale un tick y cuánto margen pide.">
    <meta name="tutorial:nivel" content="básico">
    <meta name="tutorial:fecha" content="2026-11-10">
    <meta name="tutorial:estado" content="listo">   (opcional: listo | progreso)

- Si el archivo coincide con un tema planeado en rutas.json, ese tema pasa a listo.
- Si no está en el plan, se agrega a su ruta como tema nuevo.
- Los temas planeados sin archivo quedan como pendientes.

Uso:  python3 scripts/generar_catalogo.py         (escribe catalogo.json)
      python3 scripts/generar_catalogo.py --check (solo valida, no escribe)
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTAS = RAIZ / "rutas.json"
SALIDA = RAIZ / "catalogo.json"
NIVELES = {"básico", "intermedio", "avanzado"}
ESTADOS = {"listo", "progreso"}


class LectorCabecera(HTMLParser):
    """Lee <title> y las etiquetas <meta> de un tutorial."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.titulo = ""
        self.meta: dict[str, str] = {}
        self._en_titulo = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title" and not self.titulo:
            self._en_titulo = True
        elif tag == "meta" and "name" in a:
            self.meta.setdefault(a["name"].strip().lower(), a.get("content", "").strip())

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False

    def handle_data(self, data):
        if self._en_titulo:
            self.titulo += data


def leer_tutorial(ruta: Path) -> dict:
    lector = LectorCabecera()
    lector.feed(ruta.read_text(encoding="utf-8", errors="replace"))
    return {"titulo": " ".join(lector.titulo.split()), "meta": lector.meta}


def fecha_git(rel: str) -> str | None:
    """Fecha del primer commit que agregó el archivo (AAAA-MM-DD)."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%as", "--", rel],
            cwd=RAIZ, capture_output=True, text=True, timeout=20,
        ).stdout.split()
        return out[-1] if out else None
    except Exception:
        return None


def fecha_valida(texto: str) -> bool:
    try:
        date.fromisoformat(texto)
        return True
    except ValueError:
        return False


def main(solo_validar: bool = False) -> int:
    plan = json.loads(RUTAS.read_text(encoding="utf-8"))
    avisos: list[str] = []
    salida_rutas = []

    for ruta in plan["rutas"]:
        carpeta = ruta.get("carpeta", ruta["id"])
        temas = [dict(t, estado="pendiente") for t in ruta.get("temas", [])]
        por_archivo = {t["archivo"]: t for t in temas}

        archivos = sorted((RAIZ / carpeta).glob("*.html")) if (RAIZ / carpeta).is_dir() else []
        for f in archivos:
            rel = f.relative_to(RAIZ).as_posix()
            info = leer_tutorial(f)
            meta = info["meta"]

            tema = por_archivo.get(rel)
            if tema is None:
                tema = {"titulo": info["titulo"] or f.stem.replace("-", " ").capitalize(), "archivo": rel}
                temas.append(tema)
                por_archivo[rel] = tema
            elif info["titulo"]:
                tema["titulo"] = info["titulo"]

            estado = meta.get("tutorial:estado", "listo").lower()
            if estado not in ESTADOS:
                avisos.append(f"{rel}: tutorial:estado '{estado}' no es válido; se toma como listo")
                estado = "listo"
            tema["estado"] = estado

            nivel = meta.get("tutorial:nivel", tema.get("nivel", "")).lower()
            if nivel and nivel not in NIVELES:
                avisos.append(f"{rel}: tutorial:nivel '{nivel}' no es válido (básico, intermedio, avanzado)")
            if nivel:
                tema["nivel"] = nivel

            fecha = meta.get("tutorial:fecha", "")
            if fecha and not fecha_valida(fecha):
                avisos.append(f"{rel}: tutorial:fecha '{fecha}' debe ser AAAA-MM-DD")
                fecha = ""
            tema["fecha"] = fecha or fecha_git(rel) or date.today().isoformat()

            if meta.get("description"):
                tema["descripcion"] = meta["description"]
            if not info["titulo"]:
                avisos.append(f"{rel}: falta <title>")
            if not meta.get("description"):
                avisos.append(f"{rel}: falta <meta name=\"description\">")

        salida_rutas.append({
            "id": ruta["id"],
            "titulo": ruta["titulo"],
            "descripcion": ruta.get("descripcion", ""),
            "temas": temas,
        })

    todos = [t for r in salida_rutas for t in r["temas"]]
    catalogo = {
        "titulo": plan.get("titulo", ""),
        "descripcion": plan.get("descripcion", ""),
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "totales": {
            "temas": len(todos),
            "listos": sum(t["estado"] == "listo" for t in todos),
            "progreso": sum(t["estado"] == "progreso" for t in todos),
        },
        "rutas": salida_rutas,
    }

    for a in avisos:
        print(f"AVISO  {a}")
    t = catalogo["totales"]
    print(f"{t['listos']} listos, {t['progreso']} en progreso, {t['temas']} temas en total")

    if not solo_validar:
        SALIDA.write_text(json.dumps(catalogo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Escrito {SALIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(solo_validar="--check" in sys.argv))
