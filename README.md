# ERA-Visor

Convertidor de PDFs de investigaciones ferroviarias (ERA) a Markdown estructurado.

## Uso

### Windows (doble clic)
1. Coloca `convertir_pdfs.bat` y `pdf_to_md.py` en la carpeta con los PDFs
2. Haz doble clic en `convertir_pdfs.bat`
3. Los Markdown se generan en `docs_md/`

### Línea de comandos
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

## Estructura de salida (modo ERA)
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

## Requisitos
- Python 3.10+
- PyMuPDF: `pip install pymupdf`

## Metadatos extraídos
Cada `.md` incluye frontmatter YAML con:
- País, organismo investigador, año
- Número de expediente
- Fecha y hora del suceso
- Idiomas detectados
- Secciones del informe
- Operador ferroviario
- Víctimas (fallecidos, heridos)
- Metadatos del PDF (páginas, tamaño, etc.)

## Siguiente paso
Subir `docs_md/` a Hermes y ejecutar el curador para generar datos estructurados.
