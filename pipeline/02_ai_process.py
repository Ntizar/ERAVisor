#!/usr/bin/env python3
"""
02_ai_process.py — Procesa incidentes crudos con IA y rellena incidentes_procesados

Lee la tabla incidentes_crudos, envía cada texto a la API de NaN (deepseek-v4-flash),
extrae datos estructurados siguiendo la estructura del DOCX, y los inserta en:
  - incidentes_procesados (1:1)
  - causas (1:N)
  - recomendaciones (1:N)
  - factores_coadyuvantes (1:N)
  - victimas_detalle (1:N)
  - subsistemas_afectados (1:N)
  - personal_implicado (1:N)

Uso:
    python3 02_ai_process.py
    python3 02_ai_process.py --db ../db/eravisor.db --model deepseek-v4-flash
    python3 02_ai_process.py --incidentes ERA-ES-2024-ES-10614  # Solo uno
    python3 02_ai_process.py --dry-run  # Cuenta pendientes sin procesar
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# ─── Configuración ───────────────────────────────────────────
DEFAULT_DB = os.path.join(os.path.dirname(__file__), '..', 'db', 'eravisor.db')
DEFAULT_MODEL = 'deepseek-v4-flash'
API_BASE = 'https://api.nan.builders/v1'
API_KEY_ENV = 'NAN_API'

# ─── Prompt de extracción ────────────────────────────────────
SYSTEM_PROMPT = """Eres un analista ferroviario experto en la normativa ERA (European Railway Agency).
Tu tarea es extraer datos estructurados de informes de investigación de accidentes ferroviarios.

Debes devolver SIEMPRE un JSON válido con la siguiente estructura exacta.

Para los códigos de suceso, usa la clasificación del Anexo III del RD 929/2020:
- C01: Colisión entre trenes
- C02: Colisión de tren con obstáculo
- C03: Descarrilamiento
- C04: Suceso en paso a nivel
- C05: Accidente a personas causado por material rodante en movimiento
- C06: Incendio en material rodante
- C07: Otros sucesos
- C08: Suicidio
- C09: Cuasiaccidente / incidente grave

Para causas, usa la clasificación:
- CAU01: Factor humano — personal ferroviario
- CAU02: Factor humano — usuarios / terceras personas
- CAU03: Factor técnico — material rodante
- CAU04: Factor técnico — infraestructura
- CAU05: Factor técnico — señalización y control
- CAU06: Factor normativo / organizativo
- CAU07: Factores externos
- CAU08: Causa no determinada

RESPONDE SOLO CON EL JSON. Sin markdown, sin explicaciones, sin texto adicional."""

USER_PROMPT_TPL = """Analiza el siguiente informe de accidente ferroviario y extrae los datos estructurados.

INCIDENTE: {incident_id}
PAÍS: {pais}
AÑO: {year}

TEXTO DEL INFORME:
{texto}

Devuelve un JSON con esta estructura exacta:
```json
{{
  "incidentes_procesados": {{
    "ref_informe": "",
    "codigo_interno": "",
    "fecha_informe": "",
    "version_informe": "",
    "descripcion_corta": "Texto breve (máx 200 chars)",
    "resumen_ampliado": "Resumen completo",
    "consecuencias_principales": "",
    "tipo_suceso_n1": "C01-C09 o null",
    "tipo_suceso_n2": "C01.01-C09.99 o null",
    "tipo_suceso_n3": null,
    "subtipo_nacional": "Código específico del país si aplica",
    "admin_infraestructura": "ADIF, SNCF Réseau, etc.",
    "empresa_ferroviaria": "Nombre del operador",
    "fecha_suceso": "YYYY-MM-DD",
    "hora_suceso": "HH:MM",
    "provincia": "",
    "municipio": "",
    "coordenadas_lat": null,
    "coordenadas_lon": null,
    "linea": "Nombre de la línea",
    "pk": null,
    "tramo": "",
    "tipo_via": "plena_vía / estación / terminal",
    "tipo_red": "AV / convencional / cercanías / métrico",
    "estacion": false,
    "paso_nivel": false,
    "paso_nivel_tipo": "activo_barreras / activo_sin / pasivo",
    "trafico": "viajeros / mercancías / mixto / maniobras",
    "explotacion": "nominal / degradada",
    "sistema_proteccion": "ASFA / ERTMS / LZB / ninguno",
    "tipo_tren": "Viajeros / Mercancías / Mantenimiento / Obras",
    "material_rodante_matricula": "",
    "composicion": "",
    "obras_en_tramo": false,
    "punto_riesgo_listado": false,
    "ltv_existente": "",
    "factor_humano": false,
    "factor_humano_tipo": "Adif / Adif AV / Operador / Contratista",
    "tiempo_trabajo_personal": "",
    "condiciones_medicas": false,
    "tension_fisica_psicologica": false,
    "condiciones_meteorologicas": "",
    "visibilidad": "Buena / Reducida / Nocturna",
    "iluminacion": "Natural / Artificial",
    "impacto_economico": null,
    "danos_ambientales": false,
    "antecedentes_similares": ""
  }},
  "causas": [
    {{"tipo": "directa", "codigo_n1": "CAU01", "codigo_n2": "CAU01.01", "codigo_n3": null, "descripcion": "", "orden": 1}}
  ],
  "recomendaciones": [
    {{"texto": "", "destinatario": "", "fase_ciclo_vida": "explotación", "implementador": "Adif", "orden": 1}}
  ],
  "factores_coadyuvantes": [
    {{"descripcion": "", "categoria": "tecnico/humano/organizativo/externo", "orden": 1}}
  ],
  "victimas_detalle": [
    {{"tipo_afectado": "viajeros/personal/usuarios_pn/terceros", "fallecidos": 0, "heridos_graves": 0, "heridos_leves": 0}}
  ],
  "subsistemas_afectados": [
    {{"subsistema": "Infraestructura/Energía/CMS vía/CMS a bordo/Material Rodante/Explotación/Mantenimiento/Telemáticas"}}
  ],
  "personal_implicado": [
    {{"tipo": "maquinista/regulador/mantenedor/estación", "entidad": "", "tiempo_trabajo": "", "rol_en_suceso": ""}}
  ],
  "confianza_ia": 0.85
}}
```

IMPORTANTE: 
- Si un campo no se puede determinar, usa null
- No inventes datos. Si no aparece en el texto, déjalo como null
- Para las causas, pon SOLO las que estén explícitamente mencionadas como causas en el informe
- confianza_ia: 0.0-1.0 indicando cuán seguro estás de la extracción
- Asegúrate de que el JSON sea válido (escapar comillas, sin trailing commas)
"""


def call_llm(api_key: str, model: str, system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
    """Llama a la API de NaN y devuelve la respuesta."""
    url = f"{API_BASE}/chat/completions"

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 8192,
    }).encode('utf-8')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'ERAVisor/1.0',
    }

    for attempt in range(max_retries):
        try:
            req = Request(url, data=payload, headers=headers, method='POST')
            with urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
        except URLError as e:
            print(f"  ⚠️  Error de red (intento {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Error de JSON (intento {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def parse_llm_response(response: str) -> dict:
    """Extrae el JSON de la respuesta del LLM, limpiando markdown si es necesario."""
    # Limpiar ```json ... ``` si existe
    cleaned = re.sub(r'^```(?:json)?\s*', '', response.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned.strip())

    # Intentar parsear
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Buscar el primer { y último }
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end+1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"No se pudo parsear el JSON. Respuesta:\n{cleaned[:500]}...")


def truncate_text(text: str, max_chars: int = 30000) -> str:
    """Trunca el texto manteniendo el principio (frontmatter + primeras páginas) y el final."""
    if len(text) <= max_chars:
        return text

    # Mantener frontmatter + primeras 20000 chars + últimas 10000 chars
    front = text[:20000]
    back = text[-10000:]
    return front + "\n\n[...TRUNCATED...]\n\n" + back


def process_incident(api_key: str, model: str, incident_id: str, pais: str, year: int, texto: str, db_path: str) -> dict:
    """Procesa un incidente con la IA y guarda los resultados."""
    texto_truncado = truncate_text(texto)
    user_prompt = USER_PROMPT_TPL.format(
        incident_id=incident_id,
        pais=pais,
        year=year,
        texto=texto_truncado
    )

    print(f"  🤖 Llamando a {model}...")
    response = call_llm(api_key, model, SYSTEM_PROMPT, user_prompt)
    result = parse_llm_response(response)

    # Validar estructura mínima
    if 'incidentes_procesados' not in result:
        raise ValueError("La respuesta no contiene 'incidentes_procesados'")

    # Guardar en BD
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # 1. Insertar incidentes_procesados
        proc_raw = result['incidentes_procesados']
        # A veces la IA devuelve incidentes_procesados como string JSON o como lista
        if isinstance(proc_raw, str):
            proc = json.loads(proc_raw)
        elif isinstance(proc_raw, list):
            proc = dict(proc_raw[0]) if proc_raw else {}
        else:
            proc = dict(proc_raw)  # asegurar dict mutable
        proc['id'] = incident_id
        proc['confianza_ia'] = result.get('confianza_ia', 0.5)
        proc['modelo_ia_usado'] = model
        proc['procesado_en'] = datetime.now().isoformat()

        # Convertir booleanos a int
        bool_fields = ['estacion', 'paso_nivel', 'obras_en_tramo', 'punto_riesgo_listado',
                       'factor_humano', 'condiciones_medicas', 'tension_fisica_psicologica',
                       'danos_ambientales']
        for field in bool_fields:
            if field in proc and proc[field] is not None:
                proc[field] = 1 if proc[field] else 0

        insert_procesado_sql = """
            INSERT OR REPLACE INTO incidentes_procesados (
                id, ref_informe, codigo_interno, fecha_informe, version_informe,
                descripcion_corta, resumen_ampliado, consecuencias_principales,
                tipo_suceso_n1, tipo_suceso_n2, tipo_suceso_n3, subtipo_nacional,
                admin_infraestructura, empresa_ferroviaria,
                fecha_suceso, hora_suceso,
                provincia, municipio, coordenadas_lat, coordenadas_lon,
                linea, pk, tramo, tipo_via, tipo_red,
                estacion, paso_nivel, paso_nivel_tipo,
                trafico, explotacion, sistema_proteccion,
                tipo_tren, material_rodante_matricula, composicion,
                obras_en_tramo, punto_riesgo_listado, ltv_existente,
                factor_humano, factor_humano_tipo, tiempo_trabajo_personal,
                condiciones_medicas, tension_fisica_psicologica,
                condiciones_meteorologicas, visibilidad, iluminacion,
                impacto_economico, danos_ambientales,
                antecedentes_similares,
                confianza_ia, modelo_ia_usado, procesado_en
            ) VALUES (
                :id, :ref_informe, :codigo_interno, :fecha_informe, :version_informe,
                :descripcion_corta, :resumen_ampliado, :consecuencias_principales,
                :tipo_suceso_n1, :tipo_suceso_n2, :tipo_suceso_n3, :subtipo_nacional,
                :admin_infraestructura, :empresa_ferroviaria,
                :fecha_suceso, :hora_suceso,
                :provincia, :municipio, :coordenadas_lat, :coordenadas_lon,
                :linea, :pk, :tramo, :tipo_via, :tipo_red,
                :estacion, :paso_nivel, :paso_nivel_tipo,
                :trafico, :explotacion, :sistema_proteccion,
                :tipo_tren, :material_rodante_matricula, :composicion,
                :obras_en_tramo, :punto_riesgo_listado, :ltv_existente,
                :factor_humano, :factor_humano_tipo, :tiempo_trabajo_personal,
                :condiciones_medicas, :tension_fisica_psicologica,
                :condiciones_meteorologicas, :visibilidad, :iluminacion,
                :impacto_economico, :danos_ambientales,
                :antecedentes_similares,
                :confianza_ia, :modelo_ia_usado, :procesado_en
            )
        """
        conn.execute(insert_procesado_sql, proc)

        # 2. Causas (limpiar antes)
        conn.execute("DELETE FROM causas WHERE incidente_id = ?", (incident_id,))
        for i, causa in enumerate(result.get('causas', [])):
            causa['incidente_id'] = incident_id
            causa['orden'] = i + 1
            conn.execute("""
                INSERT INTO causas (incidente_id, tipo, codigo_n1, codigo_n2, codigo_n3, descripcion, orden)
                VALUES (:incidente_id, :tipo, :codigo_n1, :codigo_n2, :codigo_n3, :descripcion, :orden)
            """, causa)

        # 3. Recomendaciones
        conn.execute("DELETE FROM recomendaciones WHERE incidente_id = ?", (incident_id,))
        for i, rec in enumerate(result.get('recomendaciones', [])):
            rec['incidente_id'] = incident_id
            rec['orden'] = i + 1
            conn.execute("""
                INSERT INTO recomendaciones (incidente_id, texto, destinatario, fase_ciclo_vida, implementador, orden)
                VALUES (:incidente_id, :texto, :destinatario, :fase_ciclo_vida, :implementador, :orden)
            """, rec)

        # 4. Factores coadyuvantes
        conn.execute("DELETE FROM factores_coadyuvantes WHERE incidente_id = ?", (incident_id,))
        for i, fac in enumerate(result.get('factores_coadyuvantes', [])):
            fac['incidente_id'] = incident_id
            fac['orden'] = i + 1
            conn.execute("""
                INSERT INTO factores_coadyuvantes (incidente_id, descripcion, categoria, orden)
                VALUES (:incidente_id, :descripcion, :categoria, :orden)
            """, fac)

        # 5. Víctimas detalle
        conn.execute("DELETE FROM victimas_detalle WHERE incidente_id = ?", (incident_id,))
        for vic in result.get('victimas_detalle', []):
            vic['incidente_id'] = incident_id
            conn.execute("""
                INSERT INTO victimas_detalle (incidente_id, tipo_afectado, fallecidos, heridos_graves, heridos_leves)
                VALUES (:incidente_id, :tipo_afectado, :fallecidos, :heridos_graves, :heridos_leves)
            """, vic)

        # 6. Subsistemas afectados
        conn.execute("DELETE FROM subsistemas_afectados WHERE incidente_id = ?", (incident_id,))
        for sub in result.get('subsistemas_afectados', []):
            sub['incidente_id'] = incident_id
            conn.execute("""
                INSERT INTO subsistemas_afectados (incidente_id, subsistema)
                VALUES (:incidente_id, :subsistema)
            """, sub)

        # 7. Personal implicado
        conn.execute("DELETE FROM personal_implicado WHERE incidente_id = ?", (incident_id,))
        for per in result.get('personal_implicado', []):
            per['incidente_id'] = incident_id
            conn.execute("""
                INSERT INTO personal_implicado (incidente_id, tipo, entidad, tiempo_trabajo, rol_en_suceso)
                VALUES (:incidente_id, :tipo, :entidad, :tiempo_trabajo, :rol_en_suceso)
            """, per)

        conn.commit()
        stats = {
            'causas': len(result.get('causas', [])),
            'recomendaciones': len(result.get('recomendaciones', [])),
            'factores': len(result.get('factores_coadyuvantes', [])),
            'confianza': result.get('confianza_ia', 0),
        }
        return stats

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_pendientes(db_path: str) -> list:
    """Obtiene incidentes crudos que aún no tienen procesado."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""
        SELECT c.id, c.pais, c.year, c.texto_completo
        FROM incidentes_crudos c
        LEFT JOIN incidentes_procesados p ON c.id = p.id
        WHERE p.id IS NULL
        ORDER BY c.pais, c.year, c.id
    """).fetchall()
    conn.close()
    return rows


def main():
    parser = argparse.ArgumentParser(description='Procesa incidentes con IA')
    parser.add_argument('--db', default=DEFAULT_DB)
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--incidentes', nargs='*', help='IDs específicos a procesar')
    parser.add_argument('--dry-run', action='store_true', help='Solo contar pendientes')
    parser.add_argument('--max', type=int, default=0, help='Máx incidentes a procesar (0=todos)')
    args = parser.parse_args()

    api_key = os.environ.get(API_KEY_ENV)
    if not api_key and not args.dry_run:
        print(f"❌ Variable de entorno {API_KEY_ENV} no encontrada")
        sys.exit(1)

    db_path = os.path.abspath(args.db)
    if not os.path.exists(db_path):
        print(f"❌ BD no encontrada: {db_path}")
        print("   Ejecuta primero: python3 01_extract_raw.py --setup")
        sys.exit(1)

    # Obtener pendientes
    pendientes = get_pendientes(db_path)
    print(f"📊 Incidentes crudos sin procesar: {len(pendientes)}")

    # Filtrar por IDs específicos
    if args.incidentes:
        pendientes = [p for p in pendientes if p[0] in args.incidentes]
        print(f"   Filtrando a {len(pendientes)} específicos")

    if args.dry_run:
        print(f"\n🔍 Dry-run: {len(pendientes)} incidentes pendientes:")
        for p in pendientes:
            print(f"   • {p[0]} ({p[1]}, {p[2]}) — {len(p[3])} chars")
        return

    if not pendientes:
        print("✅ No hay incidentes pendientes de procesar")
        return

    total = len(pendientes)
    if args.max > 0:
        pendientes = pendientes[:args.max]
        print(f"   Procesando {len(pendientes)} de {total} (--max={args.max})")

    print(f"\n{'='*60}")
    print(f"🧠 Procesando {len(pendientes)} incidentes con {args.model}")
    print(f"{'='*60}\n")

    ok = 0
    errors = []

    for i, (incident_id, pais, year, texto) in enumerate(pendientes):
        print(f"\n[{i+1}/{len(pendientes)}] {incident_id} ({pais}, {year})")
        print(f"   📄 {len(texto)} chars")

        try:
            stats = process_incident(api_key, args.model, incident_id, pais, year, texto, db_path)
            print(f"   ✅ Procesado — causas: {stats['causas']}, "
                  f"recomendaciones: {stats['recomendaciones']}, "
                  f"factores: {stats['factores']}, "
                  f"confianza: {stats['confianza']:.2f}")
            ok += 1
        except Exception as e:
            errors.append((incident_id, str(e)))
            print(f"   ❌ Error: {e}")

    print(f"\n{'='*60}")
    print(f"📊 Resumen: {ok}/{len(pendientes)} procesados correctamente")
    if errors:
        print(f"❌ {len(errors)} errores:")
        for eid, err in errors[:5]:
            print(f"   • {eid}: {err}")
    print(f"{'='*60}")

    # Estadísticas finales
    conn = sqlite3.connect(db_path)
    total_proc = conn.execute("SELECT COUNT(*) FROM incidentes_procesados").fetchone()[0]
    total_causas = conn.execute("SELECT COUNT(*) FROM causas").fetchone()[0]
    total_recs = conn.execute("SELECT COUNT(*) FROM recomendaciones").fetchone()[0]
    by_pais = conn.execute("""
        SELECT c.pais, COUNT(*) FROM incidentes_procesados p
        JOIN incidentes_crudos c ON p.id = c.id
        GROUP BY c.pais
    """).fetchall()
    conn.close()

    print(f"\n📊 BD final:")
    print(f"   • incidentes_procesados: {total_proc}")
    print(f"   • causas: {total_causas}")
    print(f"   • recomendaciones: {total_recs}")
    for p, c in by_pais:
        print(f"   • {p}: {c}")


if __name__ == '__main__':
    main()