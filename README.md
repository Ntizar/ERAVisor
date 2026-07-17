# 🚆 ERAVisor — Base de Datos Global de Accidentes Ferroviarios Europeos

[![ERA](https://img.shields.io/badge/datos-ERA%20European%20Railway%20Agency-2563eb)](https://www.era.europa.eu/era-folder/accident-investigation-reports)
[![Licencia](https://img.shields.io/badge/licencia-MIT-f97316)](LICENSE)
[![SQLite](https://img.shields.io/badge/BD-SQLite-2563eb)]()
[![IA](https://img.shields.io/badge/procesado-IA%20deepseek--v4--flash-f97316)]()

**Base de datos estructurada de todos los informes de investigación de accidentes ferroviarios europeos de la ERA**, con datos extraídos por IA y clasificación normalizada según el Anexo III del RD 929/2020.

---

## 📋 Estado actual

| Fase | Estado | Datos |
|------|--------|-------|
| 🧪 Piloto ES+FR | ✅ Completado | 26 incidentes (19 ES + 7 FR) |
| 🌍 Europa | ⏳ Pendiente | 28 países, ~4000 informes |
| 👁️ Visor web | 📅 Futuro | Sobre la base de datos |
| 🔬 Fase II (externas) | 📅 Futuro | AEMET, Copernicus, etc. |

## 🗂️ Estructura del proyecto

```
ERAVisor/
├── db/                      # Base de datos SQLite
│   ├── eravisor.db          #   BD con 26 incidentes procesados
│   └── schema.sql           #   DDL de las 9 tablas
├── pipeline/                # Procesamiento
│   ├── 01_extract_raw.py    #   Parser de MDs → tabla crudos
│   ├── 02_ai_process.py     #   IA → tabla procesados + relacionadas
│   └── explorer.py          #   Consultas y estadísticas
├── rawdata/                 # Datos fuente (MDs por país/año)
│   ├── ES/                  #   España (2006-2025)
│   └── FR/                  #   Francia (2021-2023)
├── spec/
│   └── DATABASE_SPEC.md     # Especificación completa de la BD
├── notes/                   # Notas de aprendizaje
├── SESIONES.md              # 📓 Diario de sesiones del proyecto
├── INVESTIGACION.md         # Investigación técnica del pipeline PDF
├── INFORME_ESTRUCTURA_PDFS.md # Estructura de la web de la ERA
└── README.md                # Este archivo
```

## 🗄️ Esquema de la base de datos

**9 tablas** relacionadas por `incident_id` (formato: `ERA-{PAIS}-{AÑO}-{REF}`):

| Tabla | Tipo | Descripción |
|-------|------|-------------|
| `incidentes_crudos` | Principal | Datos sin procesar desde los MDs |
| `incidentes_procesados` | Principal | Datos estructurados por IA |
| `causas` | 1:N | Hasta 8 causas por incidente |
| `recomendaciones` | 1:N | Hasta 7 recomendaciones por incidente |
| `factores_coadyuvantes` | 1:N | Factores técnicos/humanos/organizativos |
| `victimas_detalle` | 1:N | Desglose por tipo de afectado |
| `subsistemas_afectados` | 1:N | Infraestructura, CMS, Explotación... |
| `personal_implicado` | 1:N | Maquinistas, reguladores, etc. |
| `incidentes_revision` | 1:N | Capa de aportaciones humanas |

Ver `spec/DATABASE_SPEC.md` para la especificación completa.

## 🔧 Pipeline

### 1. Extracción (`01_extract_raw.py`)

```bash
python3 pipeline/01_extract_raw.py --pais ES,FR --anos 2021-2025
```

Lee los MDs de `rawdata/`, parsea el frontmatter YAML, y los inserta en `incidentes_crudos`.

### 2. Procesado con IA (`02_ai_process.py`)

```bash
NAN_API="sk-..." python3 pipeline/02_ai_process.py
```

Envía cada texto a la API de NaN (deepseek-v4-flash), extrae datos estructurados siguiendo la plantilla del DOCX de la ERA, y rellena las 7 tablas relacionadas.

Opciones:
- `--incidentes ERA-ES-2024-ES-10614` — Solo un incidente específico
- `--dry-run` — Contar pendientes sin procesar
- `--max 5` — Procesar solo N incidentes

### 3. Consulta (`explorer.py`)

```bash
python3 pipeline/explorer.py                    # Resumen general
python3 pipeline/explorer.py --incidente <ID>   # Detalle completo
python3 pipeline/explorer.py --estadisticas     # Estadísticas
python3 pipeline/explorer.py --sql "SELECT ..." # SQL directo
python3 pipeline/explorer.py --export-csv       # Exportar a CSV
```

## 📊 Datos actuales (piloto ES+FR)

| Métrica | Valor |
|---------|-------|
| Incidentes procesados | 26 (19 ES + 7 FR) |
| Causas extraídas | 54 |
| Recomendaciones | 99 |
| Factores coadyuvantes | 111 |
| Víctimas (detalle) | 5F / 7G / 35L |
| Confianza IA media | 0.90 |
| Factor humano presente | 69% |

### Por país y año

| País | 2021 | 2022 | 2023 | 2024 | 2025 |
|------|------|------|------|------|------|
| 🇪🇸 España | 6 | 5 | 3 | 3 | 2 |
| 🇫🇷 Francia | 5 | 1 | 1 | — | — |

### Tipos de suceso más comunes

- **C07** (Otros sucesos): 10 — principalmente rebases de señal
- **C03** (Descarrilamientos): 4
- **C04** (Paso a nivel): 3
- **C01** (Colisión entre trenes): 2
- **C02** (Colisión con obstáculo): 2
- **C09** (Cuasiaccidente): 2
- **C06** (Incendio): 1

## 📓 Diario de sesiones

Cada sesión del proyecto se registra en **[SESIONES.md](./SESIONES.md)**, con decisiones, problemas y próximos pasos.

## 🗺️ Hoja de ruta

1. ✅ **Piloto ES+FR** — Base de datos, pipeline, IA
2. ⏳ **Europa** — Escalar a los 28 países (pipeline reutilizable)
3. 📅 **Visor web** — Dashboard interactivo sobre la BD
4. 📅 **Fase II** — Circunstancias externas (meteo, geología, etc.)
5. 📅 **Revisiones humanas** — Capa de calidad sobre los datos IA

---

Hecho con ❤️ por David Antizar — Datos: [European Railway Agency (ERA)](https://www.era.europa.eu/era-folder/accident-investigation-reports)