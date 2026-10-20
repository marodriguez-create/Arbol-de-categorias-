"""Árbol de categorías Febeca en Streamlit.

Muestra index.html con los datos de arbol.json (o de un Excel que subas en la barra lateral).
Ejecutar en local:  streamlit run streamlit_app.py
"""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from excel_a_json import convertir

BASE = Path(__file__).resolve().parent

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


@st.cache_data
def leer_json(ruta: str, mtime: float):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


@st.cache_data
def leer_html(ruta: str, mtime: float):
    return Path(ruta).read_text(encoding="utf-8")


html_path = buscar("index.html")
if not html_path:
    st.error("No encuentro index.html en el repositorio. Súbelo en la misma carpeta que streamlit_app.py.")
    st.stop()

# ---------- datos ----------
with st.sidebar:
    st.header("Datos")
    subido = st.file_uploader("Subir Excel nuevo (.xlsx)", type=["xlsx"])
    st.caption(
        "El Excel que subas aquí se ve mientras esta pestaña esté abierta. "
        "Para que quede para todos, descarga el arbol.json y súbelo al repositorio de GitHub."
    )

datos = None
if subido is not None:
    try:
        datos = convertir(subido, nombre=subido.name)
        st.sidebar.success(f"{datos['meta']['rows']:,} códigos leídos de {subido.name}".replace(",", "."))
    except Exception as e:  # noqa: BLE001
        st.sidebar.error(f"No pude leer el Excel: {e}")

if datos is None:
    json_path = buscar("data/arbol.json", "arbol.json")
    if json_path:
        datos = leer_json(str(json_path), json_path.stat().st_mtime)
    else:
        excel = buscar("data/Libro1.xlsx", "Libro1.xlsx")
        if excel:
            datos = convertir(str(excel))

if datos:
    st.sidebar.download_button(
        "Descargar arbol.json",
        data=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
        file_name="arbol.json",
        mime="application/json",
    )

# ---------- página ----------
html = leer_html(str(html_path), html_path.stat().st_mtime)
semilla = json.dumps(datos or {}, ensure_ascii=False).replace("</", "<\\/")
inyectar = f"<script>window.__ARBOL_SEED = {semilla};</script>"
if "<body>" in html:
    html = html.replace("<body>", "<body>\n" + inyectar, 1)
else:
    html = inyectar + html

components.html(html, height=2200, scrolling=True)
