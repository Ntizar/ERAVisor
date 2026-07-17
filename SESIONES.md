# 📓 ERAVisor — Diario de sesiones

> Bitácora del proyecto: cada sesión registra qué se hizo, decisiones tomadas, problemas encontrados y próximos pasos.
> Formato: `YYYY-MM-DD — Título descriptivo`

---

## [S01] 2026-07-17 — Base de datos global y procesado con IA (ES + FR piloto)

### Objetivo
Quitar el ruido del proyecto: pasar de MDs sueltos a una base de datos SQLite estructurada con 3 capas (crudos → IA → revisión humana), procesando España y Francia como piloto.

### Qué se hizo

1. **Diseño de la base de datos** (9 tablas, relaciones 1:N)
   - `incidentes_crudos` — datos sin procesar desde los MDs
   - `incidentes_procesados` — datos estructurados por IA (1:1 con crudos)
   - `causas` (1:N), `recomendaciones` (1:N), `factores_coadyuvantes` (1:N)
   - `victimas_detalle` (1:N), `subsistemas_afectados` (1:N), `personal_implicado` (1:N)
   - `incidentes_revision` (1:N) — capa de aportaciones humanas
   - Basado en la estructura del DOCX de informe de investigación ERA + Anexo III RD 929/2020

2. **Pipeline 01_extract_raw.py** — Parser de MDs
   - Lee frontmatter YAML de los MDs
   - Extrae metadatos (fecha, hora, víctimas, operador, etc.)
   - Detecta secciones del informe
   - Filtra archivos residuales (FR-100~2.PDF.md, etc.)

3. **Pipeline 02_ai_process.py** — Procesador con IA
   - Envía cada texto a NaN API (deepseek-v4-flash)
   - Extrae campos estructurados siguiendo la plantilla del DOCX
   - Rellena automáticamente las 7 tablas relacionadas
   - Manejo de truncado para textos > 30K chars

4. **Explorer.py** — Herramienta de consulta
   - Resumen general, detalle por incidente, estadísticas, SQL directo, export CSV

### Incidentes procesados

| País | Periodo | Procesados | Confianza IA media |
|------|---------|-----------|-------------------|
| 🇪🇸 España | 2021-2025 | 19 | 0.92 |
| 🇫🇷 Francia | 2021-2023 | 7 | 0.80 |

### Datos extraídos
- **54 causas** (media 2.1 por incidente)
- **99 recomendaciones** (media 3.8 por incidente)
- **111 factores coadyuvantes**
- **101 registros de víctimas detalle** (5 fallecidos, 7 graves, 35 leves)
- **53 subsistemas afectados**
- **Factor humano presente en 69% de los incidentes**

### Problemas encontrados

| Problema | Solución |
|----------|----------|
| IDs de FR usaban código BEA-TT (TT-2021-06) en vez de FR-10079 | Forzar código del FILENAME, no del frontmatter |
| NaN API rechazaba urllib.request (403 Forbidden) | Añadir `User-Agent: ERAVisor/1.0` |
| `incidentes_procesados` venía como string o lista según el incidente | Manejo robusto de tipos (dict/str/list) |
| Archivo residual FR-100~2.PDF.md (stub de metadatos) | Eliminado de la BD |
| 2 incidentes fallaron por asignación a string | Añadir `dict()` + detección de tipos |

### Archivos creados
- `spec/DATABASE_SPEC.md` — Especificación completa
- `db/schema.sql` — DDL de 9 tablas + vistas
- `db/eravisor.db` — Base de datos SQLite (26 incidentes)
- `pipeline/01_extract_raw.py` — Parser de MDs
- `pipeline/02_ai_process.py` — Procesador con IA
- `pipeline/explorer.py` — Explorador de BD
- `notes/2026-07-17-base-datos-global.md` — Nota de aprendizaje
- Este diario: `SESIONES.md`

### Archivos eliminados (obsoletos)
- `data/` — CSVs, JSONs, índices antiguos
- `scripts/` — Pipelines antiguos (extract_v2, cron_master, download_pdfs, etc.)
- `index.html` — Visor web antiguo (obsoleto, se hará nuevo)
- `notes/README.md`, `notes/2026-07-06-eravisor-sesion1.md`
- `SCHEMA.md` (reemplazado por `spec/DATABASE_SPEC.md`)

### Próximos pasos
- [ ] Añadir más países (IT, DE, UK, NL...)
- [ ] Normalizar coordenadas geográficas (Nominatim/ORS)
- [ ] Nuevo visor web con filtros sobre la BD
- [ ] Fase II: circunstancias externas (AEMET, Copernicus)
- [ ] Revisiones humanas en `incidentes_revision`

---

## Plantilla para próximas sesiones

```markdown
## [SXX] YYYY-MM-DD — Título

### Objetivo

### Qué se hizo

### Decisiones tomadas

### Problemas encontrados

### Próximos pasos
```