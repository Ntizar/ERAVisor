# ERAVisor — Sesión 1 (06/07/2026)

## Logrado
- **6 países indexados** desde ERA: ES (375), DE (392), FR (119), IT (100), NL (21), UK (373) = **1.380 informes**
- **Anexo III RD 929/2020** extraído y codificado como taxonomía lookup (sucesos + causas)
- **Anexo I definiciones** extraído (559 líneas)
- **Esquema 57 columnas** diseñado (6 secciones)
- **Pipeline Python** funcional: descarga → PyPDF2 → LLM (deepseek-v4-flash) → CSV/Excel
- **13 PDFs españoles descargados** como prueba de concepto

## Pendiente
- [ ] Descarga masiva 375 PDFs España (~2-3GB)
- [ ] Extracción LLM completa → CSV/Excel España
- [ ] Indexar resto de países ERA (~22 más)
- [ ] Pipeline multilingüe (FR, DE, IT, NL, UK)
- [ ] Dataset consolidado europeo
- [ ] Visor web global (mapa + filtros + estadísticas)

## Pipeline
`/root/workspace/ERAVisor/scripts/extract_pipeline.py`
```bash
python3 extract_pipeline.py --pais ES --samples 5  # prueba
python3 extract_pipeline.py --pais ES               # completo
```

## Taxonomía lookup
- Sucesos: 79 códigos (3 niveles de anidación)
- Causas: 53 códigos (3 niveles)
- Víctimas desglosadas: viajeros, personal, usuarios PN, terceros

## Próximos pasos recomendados
1. Lanzar extracción España en background (tarda horas)
2. Indexar resto de países
3. Construir visor web