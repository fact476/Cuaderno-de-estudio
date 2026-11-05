# Laboratorio de mercados

Plan de estudio personal de trading, futuros, gestión del riesgo, automatización, IA aplicada y
seguridad informática, con tutoriales interactivos.

**Sitio:** https://fact476.github.io/estudio-trading/

## Estructura

```
index.html                 menú principal (lee catalogo.json)
rutas.json                 plan de estudio: capítulos y temas planeados
catalogo.json              generado por el script, no se edita a mano
plantilla.html             base para tutoriales nuevos
scripts/generar_catalogo.py
analisis-tecnico/, ia/, …  un .html por tutorial, en la carpeta de su capítulo
```

## Agregar un tutorial

1. Copiar `plantilla.html` a la carpeta del capítulo con el nombre del tema.
2. Ajustar `<title>`, la descripción, el nivel y la fecha en el `<head>`.
3. `python3 scripts/generar_catalogo.py`
4. Commit y push a `main`. GitHub Actions regenera el catálogo y publica.

## Ver en local

```
python3 -m http.server 8000
```

y abrir http://localhost:8000

---
Material de estudio personal. No es asesoría financiera.
