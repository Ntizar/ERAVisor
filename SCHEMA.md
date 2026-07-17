# ERA-visor — Esquema Completo de Datos (57+ columnas)

> Schema v1.0 — 16 julio 2026
> 3 capas: RAW → CURADO → ENRIQUECIDO

---

## 📐 Principios de diseño

1. **Un registro = un informe de accidente** — desnormalizado para CSV, normalizado en SQLite
2. **Campos en español** (el cliente es español, el frontend será en español)
3. **Tres niveles de calidad** — cada campo sabe si es raw, curado o enriquecido
4. **Multilingüe** — el texto original se preserva, los campos curados van en español/inglés
5. **Taxonomía RD 929/2020** — 79 códigos de suceso + 53 códigos de causa

---

## SECCIÓN 1: IDENTIFICACIÓN (10 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 1 | `id_eravisor` | TEXT PK | `ERA-ES-2009-001` | Generado | raw |
| 2 | `era_id` | TEXT | `IT-10446` | Portada PDF | raw |
| 3 | `pais` | TEXT(2) | `ES` | Ruta carpeta | raw |
| 4 | `organismo` | TEXT | `CIAF`, `BEU`, `BEA-TT`, `RAIB`, `UIF` | Config país | raw |
| 5 | `year` | INT | `2009` | Ruta carpeta | raw |
| 6 | `expediente` | TEXT | `0062/2009` | Portada PDF | raw |
| 7 | `titulo` | TEXT | `Colisión de dos trenes en la estación de...` | Portada PDF | curado |
| 8 | `pdf_url` | TEXT | `https://.../...pdf` | Scraper | raw |
| 9 | `pdf_local` | TEXT | `pdfs/ES/2009/0062-2009.pdf` | Descarga | raw |
| 10 | `md_local` | TEXT | `docs_md/ES/2009/0062-2009.md` | pdf_to_md | raw |

## SECCIÓN 2: FECHA Y HORA (4 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 11 | `fecha_suceso` | DATE | `2009-03-15` | Regex/LLM | curado |
| 12 | `hora_suceso` | TIME | `08:30` | Regex/LLM | curado |
| 13 | `fecha_informe` | DATE | `2009-06-20` | Metadatos PDF | raw |
| 14 | `fecha_publicacion_era` | DATE | `2009-07-01` | ERA web | raw |

## SECCIÓN 3: UBICACIÓN (8 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 15 | `estacion` | TEXT | `Madrid Chamartín` | Regex/LLM | curado |
| 16 | `region` | TEXT | `Comunidad de Madrid` | Config país | curado |
| 17 | `provincia` | TEXT | `Madrid` | Regex/LLM | curado |
| 18 | `lat` | FLOAT | `40.472` | Geocodificación | curado |
| 19 | `lng` | FLOAT | `-3.682` | Geocodificación | curado |
| 20 | `pk` | TEXT | `20+350` | Regex | raw |
| 21 | `linea` | TEXT | `Madrid-Barcelona` | Regex/LLM | curado |
| 22 | `pais_region` | TEXT | `ES-MD` | ISO 3166-2 | curado |

## SECCIÓN 4: INFRAESTRUCTURA (4 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 23 | `tipo_via` | TEXT | `doble_via`, `via_unica`, `via_apartadero` | LLM | curado |
| 24 | `electrificacion` | TEXT | `si`, `no`, `desconocido` | LLM | curado |
| 25 | `tramo_velocidad` | TEXT | `alta_velocidad`, `convencional`, `cercanias` | Config línea | enriquecido |
| 26 | `tipo_trafico` | TEXT | `mixto`, `viajeros`, `mercancías`, `solo_viajeros` | Config línea | enriquecido |

## SECCIÓN 5: ENTIDADES (3 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 27 | `operador` | TEXT | `Renfe Viajeros`, `DB Fernverkehr`, `SNCF Voyageurs` | LLM | curado |
| 28 | `infraestructura` | TEXT | `ADIF`, `DB Netz`, `SNCF Réseau`, `Network Rail`, `RFI` | LLM | curado |
| 29 | `otras_entidades` | TEXT[] | `["AESF","Renfe Mercancías"]` | LLM | curado |

## SECCIÓN 6: CLASIFICACIÓN DEL SUCESO (6 campos)

Basado en **Anexo III RD 929/2020** (79 códigos de suceso, 3 niveles)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 30 | `categoria_suceso` | TEXT | `accidente`, `incidente`, `suicidio` | LLM | curado |
| 31 | `tipo_suceso_codigo` | TEXT | `1.3.1` | LLM | curado |
| 32 | `tipo_suceso_desc` | TEXT | `Descarrilamiento` | LLM + taxonomía | curado |
| 33 | `tipo_suceso_detalle` | TEXT | `Descarrilamiento de tren de viajeros en plena vía` | LLM | curado |
| 34 | `severidad_oficial` | TEXT | `muy_grave`, `grave`, `menor` | RD 929/2022 | curado |
| 35 | `severidad_calculada` | TEXT | `muy_grave`, `grave`, `menor` | Algoritmo (víctimas) | curado |

### Taxonomía de sucesos (nivel 1) — RD 929/2020

```
1 = Accidente
  1.1 = Colisión tren con vehículo ferroviario
  1.2 = Colisión con obstáculo en gálibo
  1.3 = Descarrilamiento
  1.4 = Accidente en paso a nivel
  1.5 = Accidente a persona por material rodante
  1.6 = Incendio/explosión
  1.7 = Otros accidentes
2 = Incidente
  2.1 = Precursor (rebase señal, escape material, fallo señalización)
  2.2 = Otros precursores
  2.3 = Otros incidentes
3 = Suicidio
```

## SECCIÓN 7: CLASIFICACIÓN DE CAUSAS (4 campos)

Basado en **Anexo III RD 929/2020** (53 códigos de causa, 3 niveles)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 36 | `causa_codigo` | TEXT | `1.1.1` | LLM | curado |
| 37 | `causa_desc` | TEXT | `Factor humano — Señales` | LLM + taxonomía | curado |
| 38 | `causa_detalle` | TEXT | `El maquinista interpretó incorrectamente la señal` | LLM | curado |
| 39 | `factores_contribuyentes` | TEXT[] | `["Fatiga del maquinista","Falta de visibilidad"]` | LLM | curado |

### Taxonomía de causas (nivel 1) — RD 929/2020

```
1 = Ferrocarril
  1.1 = Factor humano (señales, bloqueo, comunicación, formación)
  1.2 = Fallo técnico (material rodante, instalaciones, infraestructura)
2 = Usuarios/entorno/otros
  2.1 = Usuarios del ferrocarril
  2.2 = Condiciones de entorno (clima, vegetación, animales)
  2.3 = Otros
  2.4 = Sin identificar
```

## SECCIÓN 8: VÍCTIMAS Y DAÑOS (5 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 40 | `fallecidos` | INT | `0` | Regex/LLM | curado |
| 41 | `heridos_graves` | INT | `0` | Regex/LLM | curado |
| 42 | `heridos_leves` | INT | `5` | Regex/LLM | curado |
| 43 | `danos_materiales` | BOOL | `true` | Regex/LLM | curado |
| 44 | `danos_descripcion` | TEXT | `Daños en locomotora y primeros vagones` | LLM | curado |

## SECCIÓN 9: ANÁLISIS (5 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 45 | `resumen` | TEXT (largo) | `Incidente operacional ocurrido...` | LLM | curado |
| 46 | `descripcion` | TEXT (muy largo) | Texto completo sección descripción | Regex | raw |
| 47 | `conclusiones` | TEXT[] | `["La causa inmediata fue...","Contribuyó la falta de..."]` | LLM | curado |
| 48 | `recomendaciones` | JSON[] | `[{numero, destinatario, texto, implementador}]` | LLM | curado |
| 49 | `lecciones_aprendidas` | TEXT | `Es necesario mejorar la formación en ERTMS` | LLM | curado |

## SECCIÓN 10: ENRIQUECIMIENTO (Fase 3) (6 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 50 | `clima_temperatura_c` | FLOAT | `12.5` | ERA5/AEMET | enriquecido |
| 51 | `clima_lluvia_mm` | FLOAT | `0.0` | ERA5/AEMET | enriquecido |
| 52 | `clima_viento_kmh` | FLOAT | `25` | ERA5/AEMET | enriquecido |
| 53 | `clima_visibilidad` | TEXT | `buena`, `reducida`, `niebla` | ERA5/AEMET | enriquecido |
| 54 | `luz_diurna` | BOOL | `true` | Calculado (hora + fecha + lat) | enriquecido |
| 55 | `densidad_poblacion_km2` | INT | `500` | Eurostat | enriquecido |

## SECCIÓN 11: CALIDAD Y METADATOS (5 campos)

| # | Campo | Tipo | Ejemplo | Origen | Capa |
|---|-------|------|---------|--------|------|
| 56 | `data_status` | TEXT | `raw`, `curado`, `enriquecido` | Pipeline | raw |
| 57 | `data_completitud` | FLOAT | `0.85` | % campos no nulos | curado |
| 58 | `ultima_actualizacion` | TIMESTAMP | `2026-07-16T15:00:00` | Pipeline | raw |
| 59 | `hash_texto_raw` | TEXT | `sha256:abc123...` | Verificación | raw |
| 60 | `notas_calidad` | TEXT | `Geocoding: fallback a estación más cercana` | Pipeline | curado |

---

## 📊 Resumen de capas

| Capa | Campos | Volumen ejemplo | Procesamiento | Tiempo estimado |
|------|--------|-----------------|---------------|-----------------|
| **RAW** | ~15 campos | PDF → MD (0.1 MB/informe) | PyMuPDF, sin IA | ~30 min (4000 PDFs) |
| **CURADO** | ~40 campos | MD → JSON estructurado (2-5 KB/informe) | Regex + LLM (deepseek) | ~6-10 horas |
| **ENRIQUECIDO** | ~6 campos adicionales | JSON → JSON enriquecido (+0.5 KB) | APIs externas (ERA5, Eurostat) | ~2-3 horas |

---

## 🗺️ Modelo SQLite (relacional)

```sql
-- Tabla principal: 60 columnas desnormalizadas para análisis rápido
CREATE TABLE informes (
    id_eravisor TEXT PRIMARY KEY,
    era_id TEXT,
    pais TEXT NOT NULL,
    organismo TEXT,
    year INTEGER NOT NULL,
    expediente TEXT,
    titulo TEXT,
    pdf_url TEXT,
    pdf_local TEXT,
    md_local TEXT,
    fecha_suceso TEXT,
    hora_suceso TEXT,
    fecha_informe TEXT,
    fecha_publicacion_era TEXT,
    estacion TEXT,
    region TEXT,
    provincia TEXT,
    lat REAL,
    lng REAL,
    pk TEXT,
    linea TEXT,
    pais_region TEXT,
    tipo_via TEXT,
    electrificacion TEXT,
    tramo_velocidad TEXT,
    tipo_trafico TEXT,
    operador TEXT,
    infraestructura TEXT,
    categoria_suceso TEXT,
    tipo_suceso_codigo TEXT,
    tipo_suceso_desc TEXT,
    tipo_suceso_detalle TEXT,
    severidad_oficial TEXT,
    severidad_calculada TEXT,
    causa_codigo TEXT,
    causa_desc TEXT,
    causa_detalle TEXT,
    fallecidos INTEGER DEFAULT 0,
    heridos_graves INTEGER DEFAULT 0,
    heridos_leves INTEGER DEFAULT 0,
    danos_materiales INTEGER DEFAULT 0,
    danos_descripcion TEXT,
    resumen TEXT,
    descripcion TEXT,
    clima_temperatura_c REAL,
    clima_lluvia_mm REAL,
    clima_viento_kmh REAL,
    clima_visibilidad TEXT,
    luz_diurna INTEGER,
    densidad_poblacion_km2 INTEGER,
    data_status TEXT DEFAULT 'raw',
    data_completitud REAL,
    ultima_actualizacion TEXT,
    hash_texto_raw TEXT,
    notas_calidad TEXT
);

-- Tabla 1:N de recomendaciones
CREATE TABLE recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    informe_id TEXT REFERENCES informes(id_eravisor),
    numero TEXT NOT NULL,
    destinatario TEXT,
    texto TEXT NOT NULL,
    implementador TEXT
);

-- Tabla 1:N de factores contribuyentes
CREATE TABLE factores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    informe_id TEXT REFERENCES informes(id_eravisor),
    factor TEXT NOT NULL,
    categoria TEXT
);

-- Tabla de entidades ferroviarias (catálogo)
CREATE TABLE entidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo TEXT,
    pais TEXT
);

-- Tabla de enriquecimiento (Fase 3)
CREATE TABLE enriquecimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    informe_id TEXT REFERENCES informes(id_eravisor),
    fuente TEXT NOT NULL,
    tipo_dato TEXT NOT NULL,
    valor TEXT,
    unidad TEXT
);
```

---

## 🔄 Pipeline de transformación

```
PDF (5.3 GB)
  │
  ▼ [pdf_to_md.py]  ← SIN IA, solo PyMuPDF
  │
MD (~400 MB) ────────────────────────────────► RAW CSV (15 columnas)
  │
  ▼ [md_to_curado.py]  ← Regex + LLM por campo
  │
CUARDO (SQLite + JSON) ─────────────────────► CURADO CSV (45 columnas)
  │
  ▼ [md_enriquecer.py]  ← APIs externas
  │
ENRIQUECIDO (SQLite + JSON) ───────────────► COMPLETO CSV (55+ columnas)
```

---

## 📁 Estructura del proyecto

```
ERAVisor/
├── SCHEMA.md              ← Este documento
├── eravisor.db            ← SQLite (fuente de verdad combinada)
├── data/
│   ├── raw/               ← CSV raw (15 cols, solo texto)
│   ├── curado/            ← JSON por informe (45 cols)
│   └── enriquecido/       ← JSON por informe (55 cols)
├── csv/
│   ├── informes.csv       ← 57 columnas, 1 fila/informe
│   ├── recomendaciones.csv← Relacional
│   ├── factores.csv       ← Relacional
│   └── estadisticas.csv   ← Agregaciones
├── docs_md/               ← Markdown de cada PDF (~400 MB)
│   ├── ES/
│   │   ├── 2009/
│   │   │   ├── 0062-2009.md
│   │   │   └── ...
│   │   └── ...
│   ├── DE/
│   └── ...
├── scripts/
│   ├── pdf_to_md.py       ← Fase 1: PDF → MD (sin IA)
│   ├── md_to_raw.py       ← Fase 1: MD → CSV raw
│   ├── md_to_curado.py    ← Fase 2: MD → JSON curado (con IA)
│   ├── export_csv.py      ← SQLite → CSV
│   └── enrich.py          ← Fase 3: APIs externas
├── schemas/
│   ├── eravisor-schema.json  ← Schema Pydantic
│   └── rd929_taxonomia.json  ← Taxonomía RD 929/2020
└── paises/                ← Configuración por país
    ├── ES.yaml            ← Patrones regex, entidades, regiones
    ├── DE.yaml
    └── ...
```
