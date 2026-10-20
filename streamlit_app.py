"""Árbol de categorías Febeca en Streamlit.

Los datos salen directamente del Excel que está en el repositorio (Libro1.xlsx).
Para actualizar la página para todos, reemplaza ese Excel en GitHub.
Ejecutar en local:  streamlit run streamlit_app.py
"""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from excel_a_json import convertir

BASE = Path(__file__).resolve().parent
EXCEL_NOMBRES = ["Libro1.xlsx", "datos.xlsx", "data/Libro1.xlsx", "data/datos.xlsx"]

st.set_page_config(page_title="Árbol de categorías Febeca", page_icon="🌳", layout="wide")
st.markdown(
    "<style>.block-container{padding-top:1rem;padding-bottom:0;max-width:100%}"
    "header[data-testid='stHeader']{height:0}</style>",
    unsafe_allow_html=True,
)


def buscar(*nombres):
    for n in nombres:
        p = BASE / n
        if p.exists():
            return p
    return None


def excel_del_repo():
    p = buscar(*EXCEL_NOMBRES)
    if p:
        return p
    # cualquier otro .xlsx que no sea la plantilla
    otros = [x for x in BASE.glob("*.xlsx") if "plantilla" not in x.name.lower()]
    return max(otros, key=lambda x: x.stat().st_mtime) if otros else None


@st.cache_data
def leer_excel(ruta: str, mtime: float):
    return convertir(ruta)


@st.cache_data
def leer_html(ruta: str, mtime: float):
    return Path(ruta).read_text(encoding="utf-8")


html_path = buscar("index.html")
if not html_path:
    st.error("No encuentro index.html en el repositorio. Súbelo en la misma carpeta que streamlit_app.py.")
    st.stop()

# ---------- datos ----------
datos, origen = None, None
excel = excel_del_repo()

with st.sidebar:
    st.header("Datos")
    if excel:
        st.write(f"La página muestra **{excel.name}**, el Excel del repositorio.")
    subido = st.file_uploader("Probar otro Excel (.xlsx)", type=["xlsx"])
    st.caption(
        f"Para cambiar los datos para todos, sube tu Excel a GitHub con el nombre "
        f"**{excel.name if excel else 'Libro1.xlsx'}**, reemplazando el anterior. "
        "El que pruebes aquí solo lo ves tú mientras esta pestaña esté abierta."
    )

if subido is not None:
    try:
        datos, origen = convertir(subido, nombre=subido.name), subido.name
        st.sidebar.success(f"{datos['meta']['rows']:,} códigos leídos de {subido.name}".replace(",", "."))
    except Exception as e:  # noqa: BLE001
        st.sidebar.error(f"No pude leer el Excel: {e}")

if datos is None and excel:
    try:
        datos, origen = leer_excel(str(excel), excel.stat().st_mtime), excel.name
    except Exception as e:  # noqa: BLE001
        st.sidebar.error(f"No pude leer {excel.name}: {e}")

if datos is None:
    json_path = buscar("data/arbol.json", "arbol.json")
    if json_path:
        datos, origen = json.loads(json_path.read_text(encoding="utf-8")), json_path.name

if not datos:
    st.sidebar.warning("No hay ningún Excel en el repositorio. Sube Libro1.xlsx a GitHub.")

# ---------- página ----------
html = leer_html(str(html_path), html_path.stat().st_mtime)
semilla = json.dumps(datos or {}, ensure_ascii=False).replace("</", "<\\/")
inyectar = f"<script>window.__ARBOL_SEED = {semilla};</script>"
if "<body>" in html:
    html = html.replace("<body>", "<body>\n" + inyectar, 1)
else:
    html = inyectar + html

if hasattr(st, "iframe"):
    st.iframe(html, height="content")  # Streamlit 1.50 o más nuevo: alto automático
else:
    components.html(html, height=2200, scrolling=True)
