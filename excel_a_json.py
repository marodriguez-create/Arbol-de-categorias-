"""Convierte un Excel de productos en data/arbol.json para el Árbol de categorías Febeca.

Uso en la consola:
    pip install openpyxl
    python excel_a_json.py Libro1.xlsx          -> escribe arbol.json

Si Streamlit ejecuta este archivo como app principal, abre la página
(streamlit_app.py) en lugar de convertir.

Columnas reconocidas (primera fila, sin importar mayúsculas ni acentos):
    categoria, subcategoria, producto  -> niveles del árbol (en ese orden)
    sku / codigo                       -> código
    marca                              -> marca
    modalidad                          -> modalidad de venta (colorea el organigrama)
    precio                             -> precio
    inventario / existencia / stock    -> inventario (unidades)
    costo                              -> costo unitario
    venta / venta_mes                  -> venta por mes (unidades)
Cualquier otra columna de texto se toma como nivel adicional.
"""
import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

CHUNK = 450


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return s.strip().lower()


def role(h):
    n = norm(h)
    if any(k in n for k in ("sku", "codigo")) or n.startswith("cod"):
        return "c"
    if "marca" in n or "proveedor" in n:
        return "m"
    if any(k in n for k in ("modalidad", "atencion", "tipo de venta", "tipo_venta", "servicio")):
        return "md"
    if any(k in n for k in ("inventario", "existencia", "stock", "disponible")):
        return "inv"
    if "venta" in n or "vta" in n:
        return "vta"
    if "costo" in n:
        return "cost"
    if any(k in n for k in ("precio", "pvp", "mayoreo")):
        return "pr"
    return "lvl"


def to_num(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 6)
    s = str(v).replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def convertir(fuente, nombre=None):
    """Lee un Excel (ruta o archivo abierto) y devuelve el dict {meta, partes}."""
    ws = openpyxl.load_workbook(fuente, data_only=True).active
    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h or "").strip() for h in next(rows_iter)]
    roles = [role(h) if h else "ign" for h in headers]
    lv = [i for i, r in enumerate(roles) if r == "lvl"]
    idx = {r: i for i, r in reversed(list(enumerate(roles))) if r not in ("lvl", "ign")}
    rows, has, last = [], {}, [""] * len(lv)
    for r in rows_iter:
        r = list(r) + [None] * (len(headers) - len(r))
        path_ = [str(r[i]).strip() if r[i] is not None else "" for i in lv]
        first = next((j for j, v in enumerate(path_) if v), None)
        if first is None:
            continue
        path_ = [last[j] if j < first else v for j, v in enumerate(path_)]
        cut = next((j for j, v in enumerate(path_) if not v), None)
        p = path_ if cut is None else path_[:cut]
        last = [p[j] if j < len(p) else "" for j in range(len(path_))]
        row = {"p": p}
        for k in ("c", "m", "md"):
            if k in idx and r[idx[k]] not in (None, ""):
                row[k] = str(r[idx[k]]).strip()
                has[k] = 1
        for k in ("pr", "inv", "cost", "vta"):
            if k in idx:
                n = to_num(r[idx[k]])
                if n is not None:
                    row[k] = n
                    has[k] = 1
        rows.append(row)
    now = datetime.now(timezone.utc)
    version = "repo" + now.strftime("%Y%m%d%H%M%S")
    n = (len(rows) + CHUNK - 1) // CHUNK
    partes = {f"p{i}": {"version": version, "i": i, "rows": rows[i * CHUNK:(i + 1) * CHUNK]} for i in range(n)}
    if nombre is None:
        nombre = Path(str(fuente)).name if isinstance(fuente, (str, Path)) else getattr(fuente, "name", "archivo.xlsx")
    meta = {
        "version": version, "chunks": n, "levels": [headers[i] for i in lv], "has": has, "extras": [],
        "filename": nombre, "updatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "rows": len(rows),
    }
    return {"meta": meta, "partes": partes}


def main(path, out="arbol.json"):
    data = convertir(path)
    Path(out).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    m = data["meta"]
    print(f"{m['rows']} códigos · niveles: {' › '.join(m['levels'])} · datos: {', '.join(m['has']) or 'ninguno'} → {out}")


def _en_streamlit():
    try:
        from streamlit.runtime import exists
        return exists()
    except Exception:
        return False


if __name__ == "__main__":
    if _en_streamlit():
        # Streamlit Cloud está usando este archivo como app principal: mostrar la página.
        import runpy
        runpy.run_path(str(Path(__file__).with_name("streamlit_app.py")), run_name="__main__")
    elif len(sys.argv) < 2:
        sys.exit("Uso: python excel_a_json.py ruta/al/archivo.xlsx")
    else:
        main(sys.argv[1])
