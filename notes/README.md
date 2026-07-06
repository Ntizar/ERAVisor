# ERAVisor — Visor Global de Accidentes Ferroviarios Europeos

## Objetivo
Crear un dataset estructurado (Excel/CSV) de todos los informes de investigación de accidentes ferroviarios de la European Union Agency for Railways (ERA), clasificados según el Anexo III del RD 929/2020, para análisis cuantitativo por país, tipo de suceso, causa, etc.

## Fuentes
- **ERA**: https://www.era.europa.eu/era-folder/accident-investigation-reports
- **RD 929/2020** (España): BOE-A-2020-13038 — Anexo I (pág 113+) y Anexo III (clasificación)

## Estructura del repo
```
ERAVisor/
├── pdfs/           # PDFs originales descargados de ERA
├── data/           # CSV/Excel estructurados por país
├── schemas/        # Documentación de esquemas y clasificaciones
├── scripts/        # Pipelines de extracción y transformación
└── visor/          # (futuro) Visor web interactivo
```

## Clasificación (Anexo III RD 929/2020)
Ver schemas/clasificacion-anexo-III.md para la taxonomía completa de:
- Sucesos (Accidentes, Incidentes, Suicidios)
- Causas directas (Factor humano, Fallo técnico, Usuarios/entorno)