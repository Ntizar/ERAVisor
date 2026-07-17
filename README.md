# 🚆 ERAVisor — Visor Global de Accidentes Ferroviarios Europeos

[![ERA](https://img.shields.io/badge/datos-ERA%20European%20Railway%20Agency-2563eb)](https://www.era.europa.eu/era-folder/accident-investigation-reports)
[![Licencia](https://img.shields.io/badge/licencia-MIT-f97316)](LICENSE)
[![España](https://img.shields.io/badge/ES-355%20informes-2563eb)]()
[![GitHub Pages](https://img.shields.io/badge/🌐-Pages%20Live-f97316)](https://ntizar.github.io/ERAVisor/)

**Dataset estructurado de todos los informes de investigación de accidentes ferroviarios de Europa**, clasificados según el Anexo III del Real Decreto 929/2020 (79 códigos de suceso + 53 causas), con visor web interactivo.

---

## 🎯 ¿Qué es esto?

ERAVisor transforma los informes narrativos en PDF de la [European Railway Agency (ERA)](https://www.era.europa.eu/era-folder/accident-investigation-reports) en datos estructurados (CSV/Excel) con clasificación normalizada, y los visualiza en un dashboard interactivo.

### Datos actuales

| País | Informes indexados | Extraídos | Período |
|------|-------------------|-----------|---------|
| 🇪🇸 España | 375 | 355 | 2006–2021 |
| 🇩🇪 Alemania | 392 | — | — |
| 🇫🇷 Francia | 119 | — | — |
| 🇮🇹 Italia | 100 | — | — |
| 🇬🇧 Reino Unido | 373 | — | — |
| 🇳🇱 Países Bajos | 21 | — | — |
| **Total** | **1.380** | **355** | — |

---

## 📊 Dashboard

[🌐 Visor en vivo →](https://ntizar.github.io/ERAVisor/)

### Características del visor

| Funcionalidad | Detalle |
|--------------|---------|
| 🗺️ **Mapa** | Leaflet + MarkerCluster, colores por gravedad |
| 📈 **Estadísticas** | 4 gráficos Chart.js reactivos a filtros |
| 📋 **Tabla** | 24 columnas, ordenable, búsqueda, paginación |
| 🔍 **Filtros** | Año, país, provincia, tipo suceso, causa |
| 📥 **Exportar** | CSV filtrado con un clic |
| 🎨 **Diseño** | Aurora DS — azul #2563eb + naranja #f97316 |

---

## 🏗️ Pipeline

```
ERA PDFs → download_pdfs.py → extract_v2.py (regex jerárquico) → 
CSV/Excel → gen_visor_data.py → visor/index.html
```

### Scripts

| Script | Función |
|--------|---------|
| `scripts/download_pdfs.py` | Descarga masiva de PDFs desde ERA |
| `scripts/extract_v2.py` | Extracción con regex jerárquico (24 campos) |
| `scripts/gen_visor_data.py` | Genera datos JS para el visor |

### Esquema de 24 campos

**Datos generales:** id_accidente, país, provincia, municipio, fecha, hora, operador, línea, pk, tipo_tráfico, tipo_vía

**Clasificación:** suceso_código, suceso_desc, causa_código, causa_desc (según Anexo III RD 929/2020)

**Víctimas:** fallecidos, heridos_graves, heridos_leves

**Análisis:** resumen, causas_directas, factores_contribuyentes, recomendaciones

---

## 📋 Taxonomía (Anexo III RD 929/2020)

### Sucesos ferroviarios
- **1. Accidente** — Colisión (1.1), Descarrilamiento (1.3), Paso a nivel (1.4), Atropello (1.5), Incendio (1.6)
- **2. Incidente** — Rotura carril (2.1.1), Señal rebasada (2.1.4), Rueda/eje roto
- **3. Suicidio** — Consumado (3.1), Intento (3.2)

### Causas directas
- **1. Ferrocarril** — Factor humano (1.1), Fallo técnico (1.2)
- **2. Usuarios/entorno** — Condiciones meteorológicas (2.2.1), Usuario PN (2.3.3)

---

## 🐍 Scripts Python

### Conversión de PDFs a Markdown

**Requisitos:** Python 3.10+, PyMuPDF (`pip install pymupdf`)

```bash
# Un solo PDF
python pdf_to_md.py --input informe.pdf --output docs_md/

# Carpeta entera (estructura ERA)
python pdf_to_md.py --input pdfs/ --output docs_md/ --era --recursive

# Carpeta plana
python pdf_to_md.py --input pdfs/ --output docs_md/ --recursive

# Solo listar (dry-run)
python pdf_to_md.py --input pdfs/ --output docs_md/ --dry-run
```

**Estructura de salida (modo ERA):**
```
docs_md/
├── ES/
│   ├── 2009/
│   │   └── ES_2009_0062.md
│   └── 2024/
│       └── ES_2024_0001.md
├── DE/
│   └── 2024/
│       └── DE_2024_10525.md
└── ...
```

Cada `.md` incluye frontmatter YAML con: país, organismo investigador, año, expediente, fecha/hora, idiomas, secciones, operador, víctimas, metadatos del PDF.

---

## 🚀 Para desarrollo local

```bash
# Clonar
git clone https://github.com/Ntizar/ERAVisor.git
cd ERAVisor

# Servir visor localmente
cd visor && python3 -m http.server 8765
# → http://localhost:8765
```

---

## 📄 Licencia

MIT © [David Antizar](https://github.com/Ntizar)

**Datos:** Informes de investigación © European Union Agency for Railways (ERA) — [Accident Investigation Reports](https://www.era.europa.eu/era-folder/accident-investigation-reports)

---

*Hecho con ❤️ por David Antizar*