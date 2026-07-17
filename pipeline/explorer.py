#!/usr/bin/env python3
"""
explorer.py — Explorador interactivo de la base de datos ERAVisor

Uso:
    python3 explorer.py                          # Resumen general
    python3 explorer.py --incidente ERA-ES-2024-ES-10614  # Detalle de un incidente
    python3 explorer.py --tabla causas           # Ver tabla completa
    python3 explorer.py --estadisticas            # Estadísticas agregadas
    python3 explorer.py --sql "SELECT * FROM v_resumen_incidentes"  # SQL directo
    python3 explorer.py --export-csv             # Exportar todo a CSV
"""

import argparse
import csv
import os
import sqlite3
import sys
from datetime import datetime

DEFAULT_DB = os.path.join(os.path.dirname(__file__), '..', 'db', 'eravisor.db')


def connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def show_resumen(conn):
    """Resumen general de la BD."""
    print("=" * 65)
    print("  📊 ERAVisor — Resumen de la Base de Datos")
    print("=" * 65)

    total_raw = conn.execute("SELECT COUNT(*) FROM incidentes_crudos").fetchone()[0]
    total_proc = conn.execute("SELECT COUNT(*) FROM incidentes_procesados").fetchone()[0]
    total_causas = conn.execute("SELECT COUNT(*) FROM causas").fetchone()[0]
    total_recs = conn.execute("SELECT COUNT(*) FROM recomendaciones").fetchone()[0]
    total_fact = conn.execute("SELECT COUNT(*) FROM factores_coadyuvantes").fetchone()[0]
    total_vic = conn.execute("SELECT COUNT(*) FROM victimas_detalle").fetchone()[0]
    total_sub = conn.execute("SELECT COUNT(*) FROM subsistemas_afectados").fetchone()[0]
    total_per = conn.execute("SELECT COUNT(*) FROM personal_implicado").fetchone()[0]
    total_rev = conn.execute("SELECT COUNT(*) FROM incidentes_revision").fetchone()[0]
    pendientes = conn.execute("""
        SELECT COUNT(*) FROM incidentes_crudos c
        LEFT JOIN incidentes_procesados p ON c.id = p.id
        WHERE p.id IS NULL
    """).fetchone()[0]

    print(f"\n📦 Tablas:")
    print(f"   • incidentes_crudos:      {total_raw:4d} registros")
    print(f"   • incidentes_procesados:  {total_proc:4d} registros")
    print(f"   • causas:                 {total_causas:4d}")
    print(f"   • recomendaciones:        {total_recs:4d}")
    print(f"   • factores_coadyuvantes:  {total_fact:4d}")
    print(f"   • victimas_detalle:        {total_vic:4d}")
    print(f"   • subsistemas_afectados:   {total_sub:4d}")
    print(f"   • personal_implicado:      {total_per:4d}")
    print(f"   • incidentes_revision:     {total_rev:4d}")
    print(f"   ⏳ Pendientes de procesar:  {pendientes:4d}")

    # Por país
    print(f"\n🌍 Por país (procesados):")
    rows = conn.execute("""
        SELECT c.pais, COUNT(*), ROUND(AVG(p.confianza_ia), 2)
        FROM incidentes_procesados p
        JOIN incidentes_crudos c ON p.id = c.id
        GROUP BY c.pais
        ORDER BY c.pais
    """).fetchall()
    for r in rows:
        print(f"   • {r['pais']}: {r['COUNT(*)']:2d} incidentes | confianza media: {r['ROUND(AVG(p.confianza_ia), 2)']}")

    # Por tipo de suceso
    print(f"\n🚦 Por tipo de suceso:")
    rows = conn.execute("""
        SELECT tipo_suceso_n1, COUNT(*) as cnt
        FROM incidentes_procesados
        WHERE tipo_suceso_n1 IS NOT NULL
        GROUP BY tipo_suceso_n1
        ORDER BY cnt DESC
    """).fetchall()
    for r in rows:
        desc = conn.execute("""
            SELECT DISTINCT descripcion_corta FROM incidentes_procesados
            WHERE tipo_suceso_n1 = ? LIMIT 1
        """, (r['tipo_suceso_n1'],)).fetchone()
        print(f"   • {r['tipo_suceso_n1']}: {r['cnt']:2d}")

    # Causas más comunes
    print(f"\n🔍 Causas más comunes:")
    rows = conn.execute("""
        SELECT codigo_n1, codigo_n2, descripcion, COUNT(*) as cnt
        FROM causas
        WHERE tipo = 'directa'
        GROUP BY codigo_n1, codigo_n2
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()
    for r in rows:
        print(f"   • {r['codigo_n1']} | {r['codigo_n2'] or ''}: {r['cnt']:2d}x — {r['descripcion'][:60] if r['descripcion'] else '(sin desc)'}")

    print(f"\n🔄 Vistas disponibles:")
    print(f"   • v_resumen_incidentes — resumen de cada incidente")
    print(f"   • v_pendientes_revision — campos pendientes de revisión humana")


def show_incidente(conn, incident_id: str):
    """Muestra detalle completo de un incidente."""
    row = conn.execute("""
        SELECT p.*, c.pais, c.year, c.filename, c.fallecidos_raw, c.heridos_graves_raw, c.heridos_leves_raw
        FROM incidentes_procesados p
        JOIN incidentes_crudos c ON p.id = c.id
        WHERE p.id = ?
    """, (incident_id,)).fetchone()

    if not row:
        print(f"❌ Incidente no encontrado: {incident_id}")
        return

    print(f"\n{'='*65}")
    print(f"  🚆 {incident_id}")
    print(f"{'='*65}")
    print(f"  País: {row['pais']} | Año: {row['year']} | Archivo: {row['filename']}")
    print(f"  Confianza IA: {row['confianza_ia']:.2f} | Modelo: {row['modelo_ia_usado']}")

    print(f"\n📋 Resumen:")
    print(f"  {row['descripcion_corta'] or '(sin descripción)'}")

    print(f"\n📅 Datos del suceso:")
    print(f"  Fecha: {row['fecha_suceso'] or '?'} | Hora: {row['hora_suceso'] or '?'}")
    print(f"  Localización: {row['provincia'] or '?'}, {row['municipio'] or '?'}")
    print(f"  Línea: {row['linea'] or '?'} | PK: {row['pk'] or '?'}")
    print(f"  Tipo vía: {row['tipo_via'] or '?'} | Red: {row['tipo_red'] or '?'}")
    print(f"  Estación: {'Sí' if row['estacion'] else 'No'} | PN: {'Sí' if row['paso_nivel'] else 'No'}")

    print(f"\n🏷️ Clasificación:")
    print(f"  Suceso: {row['tipo_suceso_n1'] or '?'} | {row['tipo_suceso_n2'] or ''}")
    print(f"  Tráfico: {row['trafico'] or '?'} | Explotación: {row['explotacion'] or '?'}")

    print(f"\n🏢 Entidades:")
    print(f"  Admin. infraestructura: {row['admin_infraestructura'] or '?'}")
    print(f"  Empresa ferroviaria: {row['empresa_ferroviaria'] or '?'}")

    print(f"\n👥 Víctimas (crudo):")
    print(f"  Fallecidos: {row['fallecidos_raw']} | Graves: {row['heridos_graves_raw']} | Leves: {row['heridos_leves_raw']}")

    # Causas
    causas = conn.execute("""
        SELECT * FROM causas WHERE incidente_id = ? ORDER BY tipo, orden
    """, (incident_id,)).fetchall()
    if causas:
        print(f"\n⚠️ Causas ({len(causas)}):")
        for c in causas:
            cod = f"{c['codigo_n1']}/{c['codigo_n2'] or ''}"
            print(f"  [{c['tipo']}] {cod:20s} {c['descripcion'][:80] or ''}")

    # Recomendaciones
    recs = conn.execute("""
        SELECT * FROM recomendaciones WHERE incidente_id = ? ORDER BY orden
    """, (incident_id,)).fetchall()
    if recs:
        print(f"\n📝 Recomendaciones ({len(recs)}):")
        for r in recs:
            print(f"  {r['orden']}. {r['texto'][:100] or ''}...")
            if r['destinatario']:
                print(f"     → Destinatario: {r['destinatario']}")

    # Factores coadyuvantes
    facs = conn.execute("""
        SELECT * FROM factores_coadyuvantes WHERE incidente_id = ? ORDER BY orden
    """, (incident_id,)).fetchall()
    if facs:
        print(f"\n🔗 Factores coadyuvantes ({len(facs)}):")
        for f in facs:
            print(f"  [{f['categoria']}] {f['descripcion'][:80] or ''}")

    # Víctimas detalle
    vics = conn.execute("""
        SELECT * FROM victimas_detalle WHERE incidente_id = ?
    """, (incident_id,)).fetchall()
    if vics:
        print(f"\n👤 Víctimas detalle:")
        for v in vics:
            print(f"  {v['tipo_afectado']}: {v['fallecidos']}F / {v['heridos_graves']}G / {v['heridos_leves']}L")

    # Subsistemas
    subs = conn.execute("""
        SELECT * FROM subsistemas_afectados WHERE incidente_id = ?
    """, (incident_id,)).fetchall()
    if subs:
        print(f"\n🔧 Subsistemas afectados: {', '.join(s['subsistema'] for s in subs)}")

    print()


def show_tabla(conn, tabla: str, limit: int = 10):
    """Muestra contenido de una tabla."""
    if tabla not in ('incidentes_crudos', 'incidentes_procesados', 'causas',
                     'recomendaciones', 'factores_coadyuvantes', 'victimas_detalle',
                     'subsistemas_afectados', 'personal_implicado', 'incidentes_revision'):
        print(f"❌ Tabla no válida: {tabla}")
        return

    rows = conn.execute(f"SELECT * FROM {tabla} LIMIT {limit}").fetchall()
    if not rows:
        print(f"📭 {tabla}: vacía")
        return

    keys = list(rows[0].keys())
    print(f"\n📋 {tabla} ({len(rows)} filas de {conn.execute(f'SELECT COUNT(*) FROM {tabla}').fetchone()[0]} totales)")
    print(f"   Columnas: {', '.join(keys)}")
    print("-" * 65)
    for row in rows:
        print(f"   {row[keys[0]]}: ", end="")
        # Mostrar solo los primeros campos relevantes
        for k in keys[1:4]:
            val = str(row[k])[:50]
            print(f" | {k}={val}", end="")
        print()


def show_estadisticas(conn):
    """Estadísticas agregadas."""
    print("\n📈 Estadísticas ERAVisor\n")

    # Incidentes por año
    print("📅 Incidentes por año:")
    rows = conn.execute("""
        SELECT c.pais, c.year, COUNT(*) as cnt
        FROM incidentes_procesados p
        JOIN incidentes_crudos c ON p.id = c.id
        GROUP BY c.pais, c.year
        ORDER BY c.pais, c.year
    """).fetchall()
    print(f"   {'País':4s} | {'Año':4s} | {'#':3s}")
    print(f"   {'-'*15}")
    for r in rows:
        print(f"   {r['pais']:4s} | {r['year']:4d} | {r['cnt']:3d}")

    # Total víctimas
    row = conn.execute("""
        SELECT SUM(fallecidos_raw) as f, SUM(heridos_graves_raw) as g, SUM(heridos_leves_raw) as l
        FROM incidentes_crudos c
        JOIN incidentes_procesados p ON c.id = p.id
    """).fetchone()
    print(f"\n⚰️ Víctimas totales: {row['f']}F / {row['g']}G / {row['l']}L")

    # Distribución por tipo
    print(f"\n🚦 Distribución por tipo de suceso:")
    rows = conn.execute("""
        SELECT tipo_suceso_n1, COUNT(*) as cnt
        FROM incidentes_procesados
        WHERE tipo_suceso_n1 IS NOT NULL
        GROUP BY tipo_suceso_n1
        ORDER BY cnt DESC
    """).fetchall()
    for r in rows:
        bar = "█" * r['cnt']
        print(f"   {r['tipo_suceso_n1']:6s} | {r['cnt']:2d} {bar}")

    # Factor humano
    row = conn.execute("SELECT COUNT(*) FROM incidentes_procesados WHERE factor_humano=1").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM incidentes_procesados").fetchone()[0]
    if total > 0:
        print(f"\n🧠 Factor humano presente en {row}/{total} ({row*100//total}%)")


def show_sql(conn, sql: str):
    """Ejecuta SQL directo."""
    try:
        rows = conn.execute(sql).fetchall()
        if not rows:
            print("📭 Sin resultados")
            return
        keys = list(rows[0].keys())
        print(f"\n📊 {len(rows)} filas")
        print(f"   Columnas: {', '.join(keys)}")
        print("-" * 65)
        for row in rows:
            vals = [f"{k}={str(row[k])[:60]}" for k in keys[:5]]
            print(f"   {' | '.join(vals)}")
    except Exception as e:
        print(f"❌ Error SQL: {e}")


def export_csv(conn, output_dir: str):
    """Exporta todas las tablas a CSV."""
    os.makedirs(output_dir, exist_ok=True)
    tables = ['incidentes_crudos', 'incidentes_procesados', 'causas',
              'recomendaciones', 'factores_coadyuvantes', 'victimas_detalle',
              'subsistemas_afectados', 'personal_implicado', 'incidentes_revision']

    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            print(f"  ⏭️  {table}: vacía, saltando")
            continue

        keys = list(rows[0].keys())
        filepath = os.path.join(output_dir, f"{table}.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(keys)
            for row in rows:
                writer.writerow([str(row[k]) for k in keys])
        print(f"  ✅ {table}: {len(rows)} filas → {filepath}")

    print(f"\n📁 Exportados a {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Explorador BD ERAVisor')
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--incidente', '-i', help='Ver detalle de un incidente')
    parser.add_argument('--tabla', '-t', help='Ver contenido de una tabla')
    parser.add_argument('--estadisticas', '-e', action='store_true', help='Estadísticas')
    parser.add_argument('--sql', '-s', help='SQL directo')
    parser.add_argument('--export-csv', '-c', metavar='DIR', nargs='?',
                        const='../export_csv', help='Exportar a CSV')
    args = parser.parse_args()

    db_path = os.path.abspath(args.db)
    if not os.path.exists(db_path):
        print(f"❌ BD no encontrada: {db_path}")
        sys.exit(1)

    conn = connect(db_path)

    if args.incidente:
        show_incidente(conn, args.incidente)
    elif args.tabla:
        show_tabla(conn, args.tabla)
    elif args.estadisticas:
        show_estadisticas(conn)
    elif args.sql:
        show_sql(conn, args.sql)
    elif args.export_csv:
        export_csv(conn, os.path.abspath(args.export_csv))
    else:
        show_resumen(conn)

    conn.close()


if __name__ == '__main__':
    main()