# Elecciones Colombia 2026 — Mapas interactivos

Mapas a nivel municipal de los resultados oficiales de la elección presidencial de Colombia 2026, generados a partir de la API pública de la Registraduría Nacional del Estado Civil.

## Mapa interactivo

🗺️ **[Ver mapa: Primera vuelta — Margen ADLE − Cepeda por municipio](https://jq-dev.github.io/elecciones-colombia-2026/)**

Cubre los 1,189 municipios del país. Cada uno coloreado según el margen entre Abelardo de la Espriella y Iván Cepeda sobre votos válidos, en bins de 10 puntos porcentuales. Las 32 capitales departamentales están marcadas.

- **Naranja** (`rgb(206, 116, 42)`): gana ADLE
- **Morado** (`rgb(133, 61, 204)`): gana Cepeda
- Tonos más oscuros = margen mayor

Hover sobre cualquier municipio para ver censo electoral, votantes, votos por candidato y participación.

## Datos

- **Fuente:** Registraduría Nacional del Estado Civil (`resultados.registraduria.gov.co`)
- **Fecha de corte:** 31 de mayo de 2026, 21:38 UTC-5 (100% de mesas escrutadas)
- **Geometrías:** Shapefile DANE de municipios

## Versión estática

- `map_2026_1V_margin.png` — versión PNG de alta resolución
- `map_2026_1V_margin.svg` — versión SVG vectorial (apta para Wikimedia Commons)

## Reproducibilidad

El código fuente del mapa interactivo y la extracción de datos están en el repositorio principal de análisis: [YSC_Elecciones](https://github.com/JQ-dev/YSC_Elecciones).

## Licencia

Datos: dominio público (resultados oficiales de la Registraduría).  
Código y visualización: CC-BY 4.0.
