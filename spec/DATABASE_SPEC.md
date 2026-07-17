# ERAVisor — Especificación de Base de Datos Global

## Visión

Base de datos SQLite que estructura todos los informes de accidentes ferroviarios europeos de la ERA (European Union Agency for Railways) en un modelo relacional de tres capas: datos crudos → datos procesados por IA → datos revisados por humanos.

## Alcance Piloto

| País | Años | Informes |
|------|------|----------|
| 🇪🇸 España (CIAF) | 2021–2025 | ~19 finales |
| 🇫🇷 Francia (BEA-TT) | 2021–2023 | ~7 finales |

## Modelo de Tablas

### Relaciones

```
incidentes_crudos (1) ──→ incidentes_procesados (1)
                                   │
                                   ├──→ causas (N)
                                   ├──→ recomendaciones (N)
                                   ├──→ factores_coadyuvantes (N)
                                   ├──→ victimas_detalle (N)
                                   ├──→ subsistemas_afectados (N)
                                   └──→ personal_implicado (N)
                                   │
                            incidentes_revision (N)
```

### Tabla: incidentes_crudos

Datos extraídos directamente del YAML frontmatter + metadatos del MD. Sin interpretación.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | TEXT PK | `ERA-{PAIS}-{YYYY}-{N}` |
| pais | TEXT | ISO 3166-1 alpha-2 |
| organismo | TEXT | CIAF, BEA-TT, BEU, RAIB... |
| year | INTEGER | Año del suceso |
| filename | TEXT | Nombre del archivo MD original |
| expediente | TEXT | Nº expediente ERA |
| fecha_suceso | TEXT | ISO 8601 |
| hora_suceso | TEXT | HH:MM |
| fallecidos_raw | INTEGER | Del frontmatter |
| heridos_graves_raw | INTEGER | Del frontmatter |
| heridos_leves_raw | INTEGER | Del frontmatter |
| operador_raw | TEXT | Del frontmatter |
| idiomas | TEXT | JSON array |
| tiene_english_summary | INTEGER | BOOL |
| secciones_detectadas | TEXT | JSON array |
| paginas | INTEGER | Del PDF |
| chars_totales | INTEGER | Del PDF |
| tamano_bytes | INTEGER | Del PDF |
| texto_completo | TEXT | MD completo |
| data_status | TEXT | 'raw' |
| procesado_en | TEXT | Timestamp ISO |

### Tabla: incidentes_procesados

Datos estructurados por IA siguiendo la estructura del DOCX de informe de investigación. Uno por incidente.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | TEXT PK FK | FK → incidentes_crudos.id |
| ref_informe | TEXT | Nº de referencia del informe |
| codigo_interno | TEXT | Código interno del suceso |
| fecha_informe | TEXT | Fecha del informe |
| version_informe | TEXT | Versión/revisión |
| descripcion_corta | TEXT | 1-2 líneas del suceso |
| resumen_ampliado | TEXT | Resumen completo sección 1 |
| consecuencias_principales | TEXT | Consecuencias principales |
| tipo_suceso_n1 | TEXT | C01-C09 (Anexo III) |
| tipo_suceso_n2 | TEXT | C01.01-C09.99 |
| tipo_suceso_n3 | TEXT | Nivel detalle adicional |
| subtipo_nacional | TEXT | Código nacional del país |
| admin_infraestructura | TEXT | ADIF, SNCF Réseau... |
| empresa_ferroviaria | TEXT | Operador/es implicados |
| fecha_suceso | TEXT | Fecha verificada |
| hora_suceso | TEXT | Hora verificada |
| provincia | TEXT | Provincia/región |
| municipio | TEXT | Municipio |
| coordenadas_lat | REAL | WGS84 |
| coordenadas_lon | REAL | WGS84 |
| linea | TEXT | Línea ferroviaria |
| pk | REAL | Punto kilométrico |
| tramo | TEXT | Tramo entre estaciones |
| tipo_via | TEXT | plena_vía, estación, terminal |
| tipo_red | TEXT | AV, convencional, cercanías, métrico |
| estacion | INTEGER | BOOL |
| paso_nivel | INTEGER | BOOL |
| paso_nivel_tipo | TEXT | activo_barreras, activo_sin, pasivo |
| trafico | TEXT | viajeros, mercancías, mixto, maniobras |
| explotacion | TEXT | nominal, degradada |
| sistema_proteccion | TEXT | ASFA, ERTMS, LZB, ninguno |
| tipo_tren | TEXT | Viajeros, Mercancías, Mantenimiento, Obras |
| material_rodante_matricula | TEXT | Matrícula(s) |
| composicion | TEXT | Composición del tren |
| obras_en_tramo | INTEGER | BOOL |
| punto_riesgo_listado | INTEGER | BOOL |
| ltv_existente | TEXT | Limitación Temporal de Velocidad |
| factor_humano | INTEGER | BOOL |
| factor_humano_tipo | TEXT | Adif, Adif AV, Operador, Contratista |
| tiempo_trabajo_personal | TEXT | Horas trabajadas del personal |
| condiciones_medicas | INTEGER | BOOL |
| tension_fisica_psicologica | INTEGER | BOOL |
| condiciones_meteorologicas | TEXT | Lluvia, nieve, viento, hielo, sismo... |
| visibilidad | TEXT | Buena, reducida, nocturna |
| iluminacion | TEXT | Natural, artificial |
| impacto_economico | REAL | EUR estimado |
| danos_ambientales | INTEGER | BOOL |
| antecedentes_similares | TEXT | Referencia a otros sucesos |
| confianza_ia | REAL | 0.0-1.0 |
| modelo_ia_usado | TEXT | deepseek-v4-flash |
| procesado_en | TEXT | Timestamp ISO |

### Tabla: causas (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| tipo | TEXT | directa, coadyuvante, subyacente |
| codigo_n1 | TEXT | CAU01-CAU08 |
| codigo_n2 | TEXT | CAU01.01-CAU08.99 |
| codigo_n3 | TEXT | Detalle adicional |
| descripcion | TEXT | Texto libre |
| orden | INTEGER | Orden de importancia |

### Tabla: recomendaciones (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| texto | TEXT | Contenido de la recomendación |
| destinatario | TEXT | A quién va dirigida |
| fase_ciclo_vida | TEXT | concepto, diseño, fabricación, explotación, retirada |
| implementador | TEXT | Adif, Operador, Ingeniería... |
| orden | INTEGER | |

### Tabla: factores_coadyuvantes (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| descripcion | TEXT | |
| categoria | TEXT | tecnico, humano, organizativo, externo |
| orden | INTEGER | |

### Tabla: victimas_detalle (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| tipo_afectado | TEXT | viajeros, personal, usuarios_pn, terceros |
| fallecidos | INTEGER | |
| heridos_graves | INTEGER | |
| heridos_leves | INTEGER | |

### Tabla: subsistemas_afectados (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| subsistema | TEXT | Infraestructura, Energía, CMS vía, CMS a bordo, Material Rodante, Explotación, Mantenimiento, Telemáticas |

### Tabla: personal_implicado (1:N)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| tipo | TEXT | maquinista, regulador, mantenedor, estación |
| entidad | TEXT | Adif, Operador, Contratista |
| tiempo_trabajo | TEXT | Horas trabajadas |
| rol_en_suceso | TEXT | Descripción |

### Tabla: incidentes_revision (1:N)

Aportaciones humanas. Cada fila = un campo corregido o completado.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| incidente_id | TEXT FK | → incidentes_procesados.id |
| tabla_objetivo | TEXT | incidentes_procesados, causas, recomendaciones... |
| campo_modificado | TEXT | Nombre del campo |
| valor_original | TEXT | Lo que puso la IA |
| valor_nuevo | TEXT | Corrección humana |
| comentario | TEXT | Explicación |
| revisor | TEXT | Nombre o ID |
| fecha_revision | TEXT | Timestamp |
| fuente | TEXT | Documento, entrevista, conocimiento propio |
| es_pendiente | INTEGER | 1 = la IA no supo rellenarlo |

## IDs de incidente

Formato: `ERA-{PAIS}-{YYYY}-{REFERENCIA}`

Ejemplos:
- `ERA-ES-2024-ES-10614`
- `ERA-FR-2021-FR-10015`

## Preguntas que responde este modelo

1. **¿Cuántos descarrilamientos en España en 2024 por fallo de infraestructura?**
   → `SELECT COUNT(*) FROM incidentes_procesados WHERE pais='ES' AND year=2024 AND tipo_suceso_n1='C03' AND id IN (SELECT incidente_id FROM causas WHERE codigo_n1='CAU04')`

2. **¿Qué operador tiene más accidentes con factor humano?**
   → `SELECT empresa_ferroviaria, COUNT(*) FROM incidentes_procesados WHERE factor_humano=1 GROUP BY empresa_ferroviaria ORDER BY COUNT(*) DESC`

3. **¿Recomendaciones a ADIF no implementadas?**
   → `SELECT r.texto FROM recomendaciones r JOIN incidentes_procesados p ON r.incidente_id=p.id WHERE r.destinatario LIKE '%Adif%'`

4. **¿Incidentes cerca de estación con víctimas?**
   → `SELECT * FROM incidentes_procesados WHERE estacion=1 AND id IN (SELECT incidente_id FROM victimas_detalle WHERE fallecidos>0)`
