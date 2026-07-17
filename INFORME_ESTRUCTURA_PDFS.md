# INFORME DE INVESTIGACIÓN: ESTRUCTURA DE PDFs DE LA ERA
## Análisis de informes de accidentes ferroviarios europeos

---

## 1. ESTRUCTURA DE LA WEB DE LA ERA

**URL base:** `https://www.era.europa.eu/era-folder/accident-investigation-reports`

La web se organiza en **3 niveles jerárquicos**:

```
ERA Root Folder
  └── Accident Investigation
        └── Accident Investigation Reports  ← página principal
              ├── ES Investigations  (España)
              ├── DE Investigations  (Alemania)
              ├── FR Investigations  (Francia)
              ├── UK Investigations  (Reino Unido)
              ├── IT Investigations  (Italia)
              └── ... (28 países en total)
                    ├── 2006           ← subcarpetas por año
                    ├── 2007
                    ├── ...
                    └── 2025
```

**Características:**
- **No hay paginación** — los años son subcarpetas separadas
- **No hay filtros** por tipo de accidente, severidad, etc.
- **No hay búsqueda** integrada para filtrar PDFs
- Cada año contiene una **tabla HTML** con columnas: `Index | Reference | Title (PDF link) | Approved | Note`
- Los PDFs se alojan en `/system/files/` o `/sites/default/files/`
- **28 países** cubiertos: AT, BE, BG, CH, CZ, DE, DK, EE, EL, ES, FI, FR, HR, HU, IE, IT, LT, LU, LV, NL, NO, PL, PT, RO, SE, SI, SK, UK (+ Serbia)

---

## 2. PDFS DESCARGADOS Y ANALIZADOS

| País | Archivo | Año | Págs | Tamaño | Texto | Idioma | Tablas |
|------|---------|-----|------|--------|-------|--------|--------|
| 🇪🇸 ES | ES-10614 - Final Report, 2024-64-0625-if | 2024 | 29 | 1.26 MB | ✅ Selectable | Español | 29 |
| 🇩🇪 DE | DE-10525 - final report excerpts v1.0 | 2024 | 9 | 0.28 MB | ✅ Selectable | Alemán/Inglés | 2 |
| 🇫🇷 FR | FR-10425 - beatt_2023_07_nuits_rapport | 2023 | 110 | 2.19 MB | ✅ Selectable | Francés | 7 |
| 🇬🇧 UK | R082020 - Rochford collision | 2020 | 59 | 1.38 MB | ✅ Selectable | Inglés | 8 |
| 🇮🇹 IT | IT-10446 - Brandizzo | 2023 | 73 | 2.04 MB | ✅ Selectable | Italiano | 11 |

**Todos los PDFs tienen texto seleccionable** — ninguno es escaneado. Los PDFs de la ERA son documentos generados digitalmente (Word, LibreOffice, InDesign).

---

## 3. ANÁLISIS DETALLADO POR PAÍS

### 🇪🇸 ESPAÑA (CIAF - Comisión de Investigación de Accidentes Ferroviarios)
- **Formato:** Muy estructurado con TOC (41 entradas), numeración 1.1, 1.2, etc.
- **Secciones:**
  1. Resumen
  2. La investigación y su contexto (decisión, ámbito, equipo, métodos)
  3. Descripción del suceso (circunstancias, víctimas, material, infraestructura)
  4. Análisis del suceso (cometidos, material, factores humanos, supervisión)
  5. Conclusiones (resumen del análisis, medidas adoptadas)
  6. Recomendaciones finales
  - **APPENDIX: ENGLISH SUMMARY** (página 25-29) — Cumple con Reglamento UE 2020/572
- **Portada:** Sí, con: CIAF logo, nº de informe (IF 64/2024), lugar, fecha, "English summary included in page 25"
- **Extracción:** Fácil con regex por la estructura numerada. El TOC permite navegar secciones.
- **Idioma:** Español + English Summary al final (5 páginas)

### 🇩🇪 ALEMANIA (BEU - Bundesstelle für Eisenbahnunfalluntersuchung)
- **Formato:** El PDF analizado es un **excerpt en inglés** del informe completo alemán
- **Portada:** Sí, con nota "Translation of an excerpt of the investigation report... The German language version is authoritative"
- **Secciones (TOC):**
  1. Summary (brief description, consequences, causes, safety recommendations)
  5. Conclusions (summary, measures taken, additional observations)
  6. Safety recommendations
- **Idioma:** El informe completo es en alemán. Los excerpts (extractos) son en inglés.
- **Particularidad:** Alemania publica **dos versiones** por accidente: (a) "final report" (alemán, completo) y (b) "final report excerpts" (inglés, solo puntos 1,5,6 del Anexo I)
- **Extracción:** Fácil. El excerpt es corto (9 páginas) pero muy denso.

### 🇫🇷 FRANCIA (BEA-TT - Bureau d'Enquêtes sur les Accidents de Transport Terrestre)
- **Formato:** Muy extenso (110 páginas), 71 entradas en TOC, estructura muy detallada
- **Secciones:**
  1. Synthèse (Summary)
  2. Constats immédiats et engagement de l'enquête
  3. Description du fait survenu
  4. Analyse du fait survenu
  5. Conclusions
  6. Recommandations de sécurité
  - Annexes (5 anexos)
- **Portada:** Sí, con título, fecha, lugar, organismo
- **Idioma:** Francés **sin English summary** (no cumple con Reglamento UE 2020/572)
- **Contenido:** 1,837 imágenes incrustadas (fotos, diagramas, capturas) — muy visual
- **Extracción:** Fácil por TOC, pero el tamaño (308K caracteres) requiere procesamiento por secciones

### 🇬🇧 REINO UNIDO (RAIB - Rail Accident Investigation Branch)
- **Formato:** Profesional, diseñado con Adobe InDesign, 59 páginas
- **Secciones (TOC):**
  - Preface, Summary, Introduction, Definitions
  - The accident (summary, context, sequence of events)
  - Background information
  - Analysis (immediate cause, causal factors, underlying factors)
  - Summary of conclusions
  - Actions taken, Recommendations, Observations
  - Appendices
- **Portada:** Sí, con: Report 08/2020, September 2020, título completo, organismo
- **Idioma:** Inglés (nativo) — sin English summary porque ya está en inglés
- **Extracción:** Fácil. Estructura muy clara con secciones bien definidas.

### 🇮🇹 ITALIA (DiGIFeMa - Ufficio per le Investigazioni Ferroviarie e Marittime)
- **Formato:** 73 páginas, generado con Microsoft Word
- **Secciones:**
  1. Sintesi (Summary)
  2. Indagine e relativo contesto
  3. Descrizione dell'evento
  4. Analisi dell'evento
  5. Conclusioni (sintesi dell'analisi, misure adottate)
  6. Raccomandazioni in materia di sicurezza
- **Portada:** Sí, con: Ministero delle infrastrutture, logo, título, identificativo ERAIL (IT-10446)
- **Idioma:** Italiano **sin English summary**
- **TOC:** No tiene TOC embebido en el PDF (a diferencia de ES, FR, UK)
- **Extracción:** Fácil, pero requiere identificar secciones por patrón de texto ya que no hay TOC embebido

---

## 4. COMPARACIÓN DE ESTRUCTURAS

### Secciones comunes (mapeadas)
| Sección | ES | DE | FR | UK | IT |
|---------|:--:|:--:|:--:|:--:|:--:|
| Summary/Resumen/Sintesi | ✅ | ✅ | ✅ | ✅ | ✅ |
| Description del suceso | ✅ | ✅ | ✅ | ✅ | ✅ |
| Analysis/Análisis | ✅ | ✅ | ✅ | ✅ | ✅ |
| Conclusions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Recommendations | ✅ | ✅ | ✅ | ✅ | ✅ |
| Contexto de investigación | ✅ | ❌ | ✅ | ❌ | ✅ |
| English Summary | ✅ | ✅(excerpt) | ❌ | N/A | ❌ |
| Tabla de Contenidos | ✅ | ✅ | ✅ | ✅ | ❌ |

### ¿Formato europeo común o cada país hace lo que quiere?
**RESPUESTA: Cada país hace lo que quiere, pero con un esqueleto común.**

La **Directiva 2004/49/CE** y el **Reglamento de Ejecución (UE) 2020/572** establecen que los informes deben cubrir:

1. **Resumen** (Summary)
2. **Hechos** (Facts of the accident/incident)
3. **Análisis** (Analysis)
4. **Conclusiones** (Conclusions)
5. **Recomendaciones** (Recommendations)

Además, el Artículo 3 del Reglamento 2020/572 exige que los puntos 1, 5 y 6 se traduzcan a un segundo idioma oficial europeo (generalmente inglés).

**Cumplimiento:**
- ✅ **ESPAÑA:** Sigue el formato al pie de la letra (1-6 numerados, English Summary como apéndice)
- ✅ **ALEMANIA:** Publica un "excerpt" en inglés con puntos 1,5,6 + el informe completo en alemán
- ⚠️ **FRANCIA:** No incluye English Summary (incumple el Reglamento)
- ✅ **REINO UNIDO:** Sigue el formato RAIB propio (más detallado), inglés nativo
- ⚠️ **ITALIA:** No incluye English Summary, estructura similar pero sin TOC

### Diferencias clave entre países:
| Aspecto | ES | DE | FR | UK | IT |
|---------|:--:|:--:|:--:|:--:|:--:|
| NIB | CIAF | BEU | BEA-TT | RAIB | DiGIFeMa |
| Extensión media | 20-30 pág | 8-15 pág (excerpt) | 50-110 pág | 40-60 pág | 50-80 pág |
| Formato secciones | 1-6 numerado | Libre (excerpt) | Numerado + anexos | Narrativo | 1-6 numerado |
| English Summary | ✅ Apéndice | ✅ Excerpt separado | ❌ Ausente | N/A (en inglés) | ❌ Ausente |
| Fotos/diagramas | Moderado | Poco | Mucho (1,837) | Moderado | Moderado (93) |
| TOC en PDF | ✅ | ✅ | ✅ | ✅ | ❌ |
| Último año | 2025 | 2025 | 2023 | 2020 | 2024 |

---

## 5. MÉTRICAS DE VOLUMEN

| País | Rango años | PDFs últimos 3 años | Est. total PDFs |
|------|:----------:|:-------------------:|:---------------:|
| ES | 2006-2025 | ~9 | ~60 |
| DE | 2006-2025 | ~38 | ~250 |
| FR | 2004-2023 | ~12 | ~80 |
| UK | 2005-2020 | ~40 | ~250 |
| IT | 2005-2024 | ~16 | ~100 |

**Tamaño medio de PDF:** ~1.5 MB (rango: 0.28 MB - 5.3 MB)
**Texto extraído medio:** ~140,000 caracteres (~30 páginas de texto)

---

## 6. RECOMENDACIONES PARA EXTRACCIÓN

### Enfoque recomendado:
1. **Scraping:** Navegar web ERA → carpeta país → carpeta año → tabla HTML → enlaces PDF
2. **Extracción de texto:** PyMuPDF (fitz) funciona perfectamente — todos los PDFs tienen texto seleccionable
3. **Estructuración:** 
   - Para ES, FR, UK: usar el TOC del PDF para identificar secciones
   - Para IT: usar patrones de texto (números de sección) ya que no tiene TOC
   - Para DE: los "excerpts" en inglés ya contienen solo Summary + Conclusions + Recommendations
4. **Idiomas:** Español, francés, italiano, alemán. El inglés solo aparece en excerpts alemanes y en UK
5. **English Summary:** Solo ES y DE lo proporcionan de forma fiable (ES en apéndice, DE como excerpt aparte)

### Dificultad: **BAJA-MEDIA**
- ✅ Todos los PDFs tienen texto seleccionable
- ✅ La mayoría tiene TOC navegable
- ✅ Estructura de secciones predecible (1-6 o similar)
- ⚠️ Cada país tiene su propio formato visual
- ⚠️ IT no tiene TOC embebido
- ⚠️ FR no tiene English Summary
- ⚠️ Idiomas variados (ES, FR, IT, DE) requieren procesamiento multilingüe

### Estrategia sugerida:
1. **Regex** para extraer secciones numeradas (funciona para ES, IT, FR)
2. **TOC del PDF** para navegar (funciona para ES, FR, UK, DE)
3. **LLM** para estandarizar el contenido extraído de diferentes formatos
4. **Traducción automática** para homogenizar a un solo idioma