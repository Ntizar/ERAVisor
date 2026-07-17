#!/usr/bin/env python3
"""
01_extract_raw.py — Extrae datos de MDs a tabla incidentes_crudos

Lee los archivos MD de rawdata/, parsea el frontmatter YAML,
y los inserta en la base de datos SQLite.

Uso:
    python3 01_extract_raw.py --pais ES,FR --anos 2021-2025
    python3 01_extract_raw.py --pais ES,FR --anos 2021-2025 --db ../db/eravisor.db
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime

# ─── Configuración ───────────────────────────────────────────
RAWDATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'rawdata')
DEFAULT_DB = os.path.join(os.path.dirname(__file__), '..', 'db', 'eravisor.db')


def parse_frontmatter(text: str) -> dict:
    """Extrae el frontmatter YAML (formato # === CLAVE: VALOR ===) de un MD."""
    data = {}
    lines = text.split('\n')
    in_frontmatter = False
    frontmatter_lines = []

    for line in lines:
        if line.strip() == '---' and not in_frontmatter:
            in_frontmatter = True
            continue
        elif line.strip() == '---' and in_frontmatter:
            break

        if in_frontmatter:
            frontmatter_lines.append(line)

    for line in frontmatter_lines:
        if line.startswith('#') or line.strip() == '':
            continue

        m = re.match(r'^(\w[\w_]*)\s*:\s*(.*)$', line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()

            # Limpiar valor
            value = value.strip('"').strip("'")

            # Parsear arrays: [ES, EN, IT]
            if value.startswith('[') and value.endswith(']'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]

            # Parsear booleanos
            if isinstance(value, str):
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False

            data[key] = value

    return data


def parse_idiomas(val):
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return val


def parse_secciones(val):
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return val


def extract_raw_data(filepath: str) -> dict:
    """Extrae datos crudos de un archivo MD."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    data = parse_frontmatter(content)
    filename = os.path.basename(filepath)

    # Extraer país y año del path
    parts = filepath.replace('\\', '/').split('/')
    pais = None
    year = None
    for i, p in enumerate(parts):
        if p == 'rawdata' and i + 1 < len(parts):
            pais = parts[i + 1]
            if i + 2 < len(parts):
                try:
                    year = int(parts[i + 2])
                except ValueError:
                    pass
            break

    # Generar ID único — FORZAR código del filename, no del frontmatter
    # El filename tiene el código ERA real (ES-10614, FR-10015, etc.)
    m = re.search(r'(ES-\d+|FR-\d+)', filename)
    exp = m.group(1) if m else (data.get('expediente', '') or data.get('id_eravisor', '') or '')

    incident_id = f"ERA-{pais}-{year}-{exp}" if exp else f"ERA-{pais}-{year}-{filename.replace('.md', '').replace(' ', '_')}"

    has_eng = data.get('has_english_summary', False)
    secciones = data.get('secciones', [])

    return {
        'id': incident_id,
        'pais': pais,
        'organismo': data.get('organismo', ''),
        'year': year,
        'filename': filename,
        'expediente': exp,
        'fecha_suceso': data.get('fecha_suceso', ''),
        'hora_suceso': data.get('hora_suceso', ''),
        'fallecidos_raw': int(data.get('fallecidos', 0) or 0),
        'heridos_graves_raw': int(data.get('heridos_graves', 0) or 0),
        'heridos_leves_raw': int(data.get('heridos_leves', 0) or 0),
        'operador_raw': str(data.get('operador', '') or ''),
        'idiomas': parse_idiomas(data.get('idiomas', [])),
        'tiene_english_summary': 1 if has_eng else 0,
        'secciones_detectadas': parse_secciones(secciones if isinstance(secciones, list) else []),
        'paginas': int(data.get('paginas', 0) or 0),
        'chars_totales': int(data.get('chars_totales', 0) or 0),
        'tamano_bytes': int(data.get('tamano_bytes', 0) or 0),
        'texto_completo': content,
        'data_status': 'raw',
        'procesado_en': datetime.now().isoformat(),
    }


def find_md_files(base_dir: str, paises: list, anos: range) -> list:
    """Encuentra archivos MD para los países y años indicados."""
    files = []
    for pais in paises:
        for ano in anos:
            dir_path = os.path.join(base_dir, pais, str(ano))
            if not os.path.isdir(dir_path):
                continue
            for fname in sorted(os.listdir(dir_path)):
                if fname.endswith('.md'):
                    # Saltar interim statements, notes d'étape, joint investigation decisions
                    skip_patterns = ['interim', 'note-etape', 'investigation.*decision',
                                     'fiche synth', 'notaavance']
                    skip = False
                    for pat in skip_patterns:
                        if re.search(pat, fname, re.IGNORECASE):
                            skip = True
                            break
                    if skip:
                        continue
                    files.append(os.path.join(dir_path, fname))
    return files


def deduplicate_files(files: list) -> list:
    """Elimina duplicados de FR (ej: FR-10015.md y FR_2021_FR-10015.md).
    Nos quedamos con el que tiene prefijo y sufijo más descriptivo."""
    groups = {}
    for fp in files:
        fname = os.path.basename(fp)
        # Extraer código base del informe
        base_match = re.search(r'(FR-\d+|ES-\d+)', fname)
        if base_match:
            base = base_match.group(1)
            if base not in groups:
                groups[base] = []
            groups[base].append(fp)

    # Elegir el mejor archivo de cada grupo
    result = []
    for base, fps in groups.items():
        if len(fps) == 1:
            result.append(fps[0])
        else:
            # Preferir el que tiene prefijo PAIS_YYYY_ y no contiene ~
            sorted_fps = sorted(fps, key=lambda x: (
                0 if '~' in os.path.basename(x) else 1,
                1 if re.match(r'[A-Z]{2}_\d{4}_', os.path.basename(x)) else 0,
                len(os.path.basename(x))
            ), reverse=True)
            result.append(sorted_fps[0])

    return result


def setup_database(db_path: str):
    """Crea las tablas si no existen."""
    schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def populate_crudos(files: list, db_path: str):
    """Inserta datos en incidentes_crudos."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL")

    insert_sql = """
        INSERT OR REPLACE INTO incidentes_crudos (
            id, pais, organismo, year, filename, expediente,
            fecha_suceso, hora_suceso,
            fallecidos_raw, heridos_graves_raw, heridos_leves_raw,
            operador_raw, idiomas, tiene_english_summary,
            secciones_detectadas, paginas, chars_totales, tamano_bytes,
            texto_completo, data_status, procesado_en
        ) VALUES (
            :id, :pais, :organismo, :year, :filename, :expediente,
            :fecha_suceso, :hora_suceso,
            :fallecidos_raw, :heridos_graves_raw, :heridos_leves_raw,
            :operador_raw, :idiomas, :tiene_english_summary,
            :secciones_detectadas, :paginas, :chars_totales, :tamano_bytes,
            :texto_completo, :data_status, :procesado_en
        )
    """

    total = len(files)
    ok = 0
    errors = []

    for i, fp in enumerate(files):
        try:
            row = extract_raw_data(fp)
            conn.execute(insert_sql, row)
            ok += 1
            print(f"  [{i+1}/{total}] ✅ {row['id']}")
        except Exception as e:
            errors.append((fp, str(e)))
            print(f"  [{i+1}/{total}] ❌ {os.path.basename(fp)} — {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Insertados {ok}/{total} registros en incidentes_crudos")
    if errors:
        print(f"❌ {len(errors)} errores:")
        for fp, err in errors[:5]:
            print(f"   - {fp}: {err}")

    return ok, errors


def main():
    parser = argparse.ArgumentParser(description='Extrae MDs a incidentes_crudos')
    parser.add_argument('--pais', default='ES,FR', help='Países separados por coma (default: ES,FR)')
    parser.add_argument('--anos', default='2021-2025', help='Rango de años (default: 2021-2025)')
    parser.add_argument('--db', default=DEFAULT_DB, help=f'Ruta a SQLite (default: {DEFAULT_DB})')
    parser.add_argument('--setup', action='store_true', help='Crear la BD desde schema.sql')
    args = parser.parse_args()

    paises = [p.strip() for p in args.pais.split(',')]

    ano_match = re.match(r'(\d{4})(?:-(\d{4}))?', args.anos)
    if ano_match:
        start = int(ano_match.group(1))
        end = int(ano_match.group(2)) if ano_match.group(2) else start
        anos = range(start, end + 1)
    else:
        anos = range(2021, 2026)

    print(f"🔍 Buscando MDs en {RAWDATA_DIR}")
    print(f"   Países: {', '.join(paises)}")
    print(f"   Años: {anos[0]}-{anos[-1]}")
    print()

    files = find_md_files(RAWDATA_DIR, paises, anos)
    files = deduplicate_files(files)

    print(f"📁 Encontrados {len(files)} informes finales únicos:")
    for fp in files:
        print(f"   • {os.path.basename(fp)}")
    print()

    if args.setup or not os.path.exists(args.db):
        os.makedirs(os.path.dirname(args.db), exist_ok=True)
        print(f"🗄️  Creando base de datos en {args.db}")
        setup_database(args.db)

    print(f"📥 Insertando datos en incidentes_crudos...")
    populate_crudos(files, args.db)

    conn = sqlite3.connect(args.db)
    count = conn.execute("SELECT COUNT(*) FROM incidentes_crudos").fetchone()[0]
    by_pais = conn.execute("SELECT pais, COUNT(*) FROM incidentes_crudos GROUP BY pais").fetchall()
    conn.close()

    print(f"\n📊 Total en BD: {count} registros")
    for p, c in by_pais:
        print(f"   • {p}: {c}")


if __name__ == '__main__':
    main()