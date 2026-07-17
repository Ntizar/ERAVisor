# 2026-07-17 — Base de Datos Global ERAVisor

## Objetivo
Quitar ruido del proyecto ERAVisor: convertir los MDs crudos de accidentes ferroviarios en una base de datos SQLite estructurada con 3 capas (crudos → IA → revisión humana).

## Qué se hizo

### Análisis del estado actual
- **ERAVisor**: proyecto con ~26 informes de accidentes de ES (2021-2025) y FR (2021-2023) extraídos de PDFs de la ERA como MDs
- Cada MD tiene frontmatter YAML (# === CLAVE: VALOR ===) + texto plano página a página
- Schema anterior: 24 campos planos en CSV, sin relaciones

### Diseño de la base de datos
- **9 tablas**: incidentes_crudos, incidentes_procesados, causas (1:N), recomendaciones (1:N), factores_coadyuvantes (1:N), victimas_detalle (1:N), subsistemas_afectados (1:N), personal_implicado (1:N), incidentes_revision (1:N)
- Todas relacionadas por `incident_id` (formato: ERA-{PAIS}-{AÑO}-{REF})
- Basado en la estructura del DOCX de informe de investigación ERA + Anexo III RD 929/2020

### Pipeline creado
1. **01_extract_raw.py**: Parser de MDs → extrae frontmatter YAML → inserta en incidentes_crudos
2. **02_ai_process.py**: Envía cada texto a NaN API (deepseek-v4-flash) → extrae datos estructurados → rellena todas las tablas relacionadas
3. **explorer.py**: Herramienta de consulta (resumen, detalle, estadísticas, SQL directo, export CSV)

### Lecciones aprendidas
- **IDs de FR**: algunos MDs de Francia tienen expediente `TT-2023-07` (BEA-TT) en vez de `FR-10425`. Hay que forzar el código del FILENAME, no del frontmatter.
- **User-Agent**: NaN API rechaza urllib.request por defecto (403 Forbidden). Hay que añadir `User-Agent: ERAVisor/1.0`.
- **Textos de 30-100K chars**: la IA procesa bien textos truncados a 30K chars (principio + final). Los informes españoles suelen ser más cortos (~60K chars) que los franceses (~300K chars).
- **Deduplicación FR**: Francia tiene archivos duplicados (con y sin prefijo `FR_2021_`). El patrón de deduplicación por código base (`FR-\d+`) funciona bien.

### Pendiente
- Procesar todos los países europeos (28) con el mismo pipeline
- Normalizar coordenadas geográficas (Nominatim/ORS)
- Añadir datos de circunstancias externas (AEMET, Copernicus) como Fase II
- Nuevo visor web sobre la BD

## Archivos creados
- `spec/DATABASE_SPEC.md` — Especificación completa del modelo
- `db/schema.sql` — DDL de las 9 tablas + vistas
- `pipeline/01_extract_raw.py` — Parser de MDs
- `pipeline/02_ai_process.py` — Procesador con IA
- `pipeline/explorer.py` — Explorador de BD
