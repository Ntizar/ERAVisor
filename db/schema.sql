-- ============================================================
-- ERAVisor Database Schema v1.0
-- Base de datos global de accidentes ferroviarios europeos
-- Basado en: Estructura Informe Investigación v2 (DOCX) + Anexo III RD 929/2020
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. INCIDENTES CRUDOS — Datos extraídos directamente del MD
-- ============================================================
CREATE TABLE IF NOT EXISTS incidentes_crudos (
    id              TEXT PRIMARY KEY,  -- ERA-{PAIS}-{YYYY}-{REF}
    pais            TEXT NOT NULL,     -- ISO 3166-1 alpha-2
    organismo       TEXT,              -- CIAF, BEA-TT, etc.
    year            INTEGER NOT NULL,
    filename        TEXT,              -- Nombre del archivo MD
    expediente      TEXT,              -- Nº expediente ERA
    fecha_suceso    TEXT,              -- ISO 8601
    hora_suceso     TEXT,              -- HH:MM
    fallecidos_raw  INTEGER DEFAULT 0,
    heridos_graves_raw INTEGER DEFAULT 0,
    heridos_leves_raw  INTEGER DEFAULT 0,
    operador_raw    TEXT,
    idiomas         TEXT,              -- JSON array
    tiene_english_summary INTEGER DEFAULT 0,
    secciones_detectadas TEXT,         -- JSON array
    paginas         INTEGER,
    chars_totales   INTEGER,
    tamano_bytes    INTEGER,
    texto_completo  TEXT,              -- MD completo
    data_status     TEXT DEFAULT 'raw',
    procesado_en    TEXT               -- Timestamp ISO
);

-- ============================================================
-- 2. INCIDENTES PROCESADOS — Datos estructurados por IA
-- ============================================================
CREATE TABLE IF NOT EXISTS incidentes_procesados (
    id                     TEXT PRIMARY KEY REFERENCES incidentes_crudos(id),

    -- Datos de control del informe
    ref_informe            TEXT,
    codigo_interno         TEXT,
    fecha_informe          TEXT,
    version_informe        TEXT,

    -- Resumen
    descripcion_corta      TEXT,
    resumen_ampliado       TEXT,
    consecuencias_principales TEXT,

    -- Clasificación del suceso (Anexo III)
    tipo_suceso_n1         TEXT,  -- C01-C09
    tipo_suceso_n2         TEXT,  -- C01.01-C09.99
    tipo_suceso_n3         TEXT,  -- Nivel adicional
    subtipo_nacional       TEXT,  -- Codificación específica del país

    -- Entidades
    admin_infraestructura  TEXT,  -- ADIF, SNCF Réseau, DB Netz...
    empresa_ferroviaria    TEXT,  -- Operador/es implicados

    -- Fecha y hora (verificadas)
    fecha_suceso           TEXT,
    hora_suceso            TEXT,

    -- Localización
    provincia              TEXT,
    municipio              TEXT,
    coordenadas_lat        REAL,
    coordenadas_lon        REAL,
    linea                  TEXT,
    pk                     REAL,
    tramo                  TEXT,
    tipo_via               TEXT,  -- plena_vía, estación, terminal
    tipo_red               TEXT,  -- AV, convencional, cercanías, métrico
    estacion               INTEGER DEFAULT 0,
    paso_nivel             INTEGER DEFAULT 0,
    paso_nivel_tipo        TEXT,  -- activo_barreras, activo_sin, pasivo
    trafico                TEXT,  -- viajeros, mercancías, mixto, maniobras
    explotacion            TEXT,  -- nominal, degradada

    -- Infraestructura y señalización
    sistema_proteccion     TEXT,  -- ASFA, ERTMS, LZB, ninguno

    -- Material rodante
    tipo_tren              TEXT,  -- Viajeros, Mercancías, Mantenimiento, Obras
    material_rodante_matricula TEXT,
    composicion            TEXT,

    -- Obras y riesgos
    obras_en_tramo         INTEGER DEFAULT 0,
    punto_riesgo_listado   INTEGER DEFAULT 0,
    ltv_existente          TEXT,

    -- Factor humano
    factor_humano          INTEGER DEFAULT 0,
    factor_humano_tipo     TEXT,  -- Adif, Adif AV, Operador, Contratista
    tiempo_trabajo_personal TEXT,
    condiciones_medicas    INTEGER DEFAULT 0,
    tension_fisica_psicologica INTEGER DEFAULT 0,

    -- Circunstancias externas
    condiciones_meteorologicas TEXT,
    visibilidad            TEXT,
    iluminacion            TEXT,

    -- Impacto económico y ambiental
    impacto_economico      REAL,
    danos_ambientales      INTEGER DEFAULT 0,

    -- Antecedentes
    antecedentes_similares TEXT,

    -- Metadatos de procesamiento
    confianza_ia           REAL DEFAULT 0.0,
    modelo_ia_usado        TEXT,
    procesado_en           TEXT
);

-- ============================================================
-- 3. CAUSAS (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS causas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    tipo            TEXT,  -- directa, coadyuvante, subyacente
    codigo_n1       TEXT,  -- CAU01-CAU08
    codigo_n2       TEXT,  -- CAU01.01-CAU08.99
    codigo_n3       TEXT,  -- Detalle adicional
    descripcion     TEXT,
    orden           INTEGER DEFAULT 0
);

CREATE INDEX idx_causas_incidente ON causas(incidente_id);
CREATE INDEX idx_causas_codigo_n1 ON causas(codigo_n1);

-- ============================================================
-- 4. RECOMENDACIONES (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS recomendaciones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    texto           TEXT,
    destinatario    TEXT,
    fase_ciclo_vida TEXT,  -- concepto, diseño, fabricación, pruebas, explotación, retirada
    implementador   TEXT,  -- Adif, Operador, Ingeniería, Contratista...
    orden           INTEGER DEFAULT 0
);

CREATE INDEX idx_recomendaciones_incidente ON recomendaciones(incidente_id);

-- ============================================================
-- 5. FACTORES COADYUVANTES (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS factores_coadyuvantes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    descripcion     TEXT,
    categoria       TEXT,  -- tecnico, humano, organizativo, externo
    orden           INTEGER DEFAULT 0
);

CREATE INDEX idx_factores_incidente ON factores_coadyuvantes(incidente_id);

-- ============================================================
-- 6. VÍCTIMAS DETALLE (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS victimas_detalle (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    tipo_afectado   TEXT,  -- viajeros, personal, usuarios_pn, terceros
    fallecidos      INTEGER DEFAULT 0,
    heridos_graves  INTEGER DEFAULT 0,
    heridos_leves   INTEGER DEFAULT 0
);

CREATE INDEX idx_victimas_incidente ON victimas_detalle(incidente_id);

-- ============================================================
-- 7. SUBSISTEMAS AFECTADOS (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS subsistemas_afectados (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    subsistema      TEXT
    -- Valores: Infraestructura, Energía, CMS vía, CMS a bordo,
    --          Material Rodante Adif, Material Rodante Operador,
    --          Explotación, Mantenimiento, Telemáticas
);

CREATE INDEX idx_subsistemas_incidente ON subsistemas_afectados(incidente_id);

-- ============================================================
-- 8. PERSONAL IMPLICADO (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS personal_implicado (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    tipo            TEXT,   -- maquinista, regulador, mantenedor, estación
    entidad         TEXT,   -- Adif, Operador, Contratista
    tiempo_trabajo  TEXT,   -- Horas trabajadas
    rol_en_suceso   TEXT    -- Descripción
);

CREATE INDEX idx_personal_incidente ON personal_implicado(incidente_id);

-- ============================================================
-- 9. REVISIONES HUMANAS (1:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS incidentes_revision (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id    TEXT NOT NULL REFERENCES incidentes_procesados(id),
    tabla_objetivo  TEXT,   -- incidentes_procesados, causas, recomendaciones...
    campo_modificado TEXT,  -- Nombre del campo
    valor_original  TEXT,   -- Lo que puso la IA
    valor_nuevo     TEXT,   -- Corrección humana
    comentario      TEXT,   -- Explicación
    revisor         TEXT,   -- Nombre o ID
    fecha_revision  TEXT,   -- Timestamp
    fuente          TEXT,   -- Documento, entrevista, conocimiento propio
    es_pendiente    INTEGER DEFAULT 0  -- 1 = IA no supo rellenarlo
);

CREATE INDEX idx_revision_incidente ON incidentes_revision(incidente_id);
CREATE INDEX idx_revision_pendiente ON incidentes_revision(es_pendiente) WHERE es_pendiente = 1;

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: resumen de cada incidente con sus causas principales
CREATE VIEW IF NOT EXISTS v_resumen_incidentes AS
SELECT
    p.id,
    c.pais,
    c.year,
    p.descripcion_corta,
    p.tipo_suceso_n1,
    p.tipo_suceso_n2,
    p.provincia,
    p.municipio,
    p.fecha_suceso,
    p.factor_humano,
    p.confianza_ia,
    (SELECT GROUP_CONCAT(causa.codigo_n1 || ':' || causa.descripcion, '; ')
     FROM causas causa WHERE causa.incidente_id = p.id AND causa.tipo = 'directa') AS causas_directas,
    (SELECT COUNT(*) FROM victimas_detalle v WHERE v.incidente_id = p.id) AS num_grupos_victimas,
    (SELECT COUNT(*) FROM recomendaciones r WHERE r.incidente_id = p.id) AS num_recomendaciones
FROM incidentes_procesados p
JOIN incidentes_crudos c ON p.id = c.id;

-- Vista: pendientes de revisión humana
CREATE VIEW IF NOT EXISTS v_pendientes_revision AS
SELECT
    r.id AS revision_id,
    p.id AS incidente_id,
    c.pais,
    c.year,
    r.tabla_objetivo,
    r.campo_modificado,
    r.valor_original,
    r.comentario,
    r.fecha_revision
FROM incidentes_revision r
JOIN incidentes_procesados p ON r.incidente_id = p.id
JOIN incidentes_crudos c ON p.id = c.id
WHERE r.es_pendiente = 1
ORDER BY c.pais, c.year;