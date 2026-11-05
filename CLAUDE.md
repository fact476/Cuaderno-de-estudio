# Cuaderno de estudio

Sitio estático en GitHub Pages con tutoriales interactivos en español. Empezó con
trading (acciones, ETFs, futuros), gestión del riesgo, automatización, IA aplicada y
seguridad informática defensiva. Publicado en https://fact476.github.io/Cuaderno-de-estudio/

## Cómo se alimenta el menú

- `rutas.json` es el plan de estudio: capítulos (rutas) y temas planeados, cada uno con su `archivo`.
- Cada tutorial es un `.html` en la carpeta de su ruta y se describe con etiquetas en `<head>`:
  `<title>`, `<meta name="description">`, `tutorial:nivel` (básico | intermedio | avanzado),
  `tutorial:fecha` (AAAA-MM-DD) y, opcional, `tutorial:estado` = `progreso`.
- `scripts/generar_catalogo.py` cruza el plan con los archivos y escribe `catalogo.json`.
  `index.html` solo lee `catalogo.json`; nunca se edita para agregar temas.
- El workflow `.github/workflows/publicar.yml` corre el generador y publica en cada push a `main`.

## Agregar un tutorial

1. Partir de `plantilla.html` (o adaptar uno existente) y guardarlo como `carpeta-de-la-ruta/nombre.html`.
   Si el tema ya está en `rutas.json`, usar exactamente su `archivo`.
2. Llenar las etiquetas meta. Incluir el enlace `../index.html` para volver al menú.
3. Correr `python3 scripts/generar_catalogo.py` y revisar que no salgan avisos.
4. Commit y push a `main`. La página se actualiza sola en uno o dos minutos.

Para agregar o reordenar temas del plan, editar `rutas.json`. No editar `catalogo.json` a mano.

## Reglas

- Un tutorial = un solo archivo `.html` autocontenido (CSS y JS adentro). Librerías solo por CDN.
- Todo en español, con datos simulados y el aviso de que no es asesoría financiera.
- El repositorio es público: nunca subir IPs, puertos, usuarios, llaves, tokens, números de cuenta,
  posiciones u órdenes reales, ni nombres de sistemas o bots propios. Los ejemplos usan cifras genéricas.
- Seguridad informática: solo contenido defensivo y práctica en equipos propios.
- Probar en local con `python3 -m http.server 8000` y abrir http://localhost:8000
