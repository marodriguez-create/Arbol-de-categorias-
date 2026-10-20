# Árbol de categorías Febeca

Página web para consultar el árbol de categorías de ferretería de Febeca: categoría › subcategoría › artículo, con código (SKU), marca y precio. También muestra inventario y venta por mes cuando el Excel trae esas columnas.

Se puede publicar gratis de dos formas: como app de **Streamlit Community Cloud** o como página de **GitHub Pages**. Todos los archivos van en la raíz del repositorio.

## Qué incluye

| Ruta | Para qué sirve |
| --- | --- |
| `streamlit_app.py` | App de Streamlit: muestra la página y permite subir un Excel desde la barra lateral. |
| `requirements.txt` | Paquetes que Streamlit Cloud instala (`streamlit`, `openpyxl`). |
| `index.html` | La página completa: indicadores, filtro por marca y las pestañas Productos, Categorías y árbol, Precios (Económico hasta $10, Medio de $10 a $40, Premium más de $40), Organigrama (con Guardar PDF), Estructura y Datos a ingresar. |
| `arbol.json` | Los datos con los que arranca la página. Hoy contiene `Libro1.xlsx`, con 948 códigos. |
| `Libro1.xlsx` | El Excel de origen. |
| `plantilla-arbol-categorias.xlsx` | Plantilla con todas las columnas que reconoce la página, incluida `modalidad`, que colorea el organigrama. |
| `excel_a_json.py` | Convierte un Excel nuevo en `arbol.json`. |

## Publicar en Streamlit Community Cloud

1. Sube todos los archivos a la raíz del repositorio de GitHub.
2. En [share.streamlit.io](https://share.streamlit.io) crea la app con **Main file path** `streamlit_app.py`.
   Si la app ya existe con `excel_a_json.py` como archivo principal, también funciona: ese archivo detecta que lo abre Streamlit y carga la página.
3. Streamlit instala lo de `requirements.txt` y abre la página con los datos de `arbol.json`.

Para cambiar los datos en Streamlit, sube el Excel en la barra lateral. Lo ves al momento. Para que quede para todos, pulsa **Descargar arbol.json** y sube ese archivo al repositorio, reemplazando el anterior.

## Publicar en GitHub Pages

1. Crea un repositorio nuevo en GitHub, por ejemplo `arbol-categorias-febeca`.
2. Sube todo el contenido de esta carpeta: arrastra los archivos en **Add file › Upload files**, o usa la consola:

   ```bash
   git init
   git add .
   git commit -m "Árbol de categorías Febeca"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/arbol-categorias-febeca.git
   git push -u origin main
   ```

3. En el repositorio entra a **Settings › Pages**. En *Source* elige **Deploy from a branch**, rama `main` y carpeta `/ (root)`, y guarda.
4. En uno o dos minutos la página queda en `https://TU-USUARIO.github.io/arbol-categorias-febeca/`.

> Si el repositorio es privado, GitHub Pages solo funciona con planes de pago (Pro, Team o Enterprise).

## Actualizar los datos

Hay dos formas:

**Para todos (recomendada).** Convierte el Excel nuevo y sube el JSON al repositorio:

```bash
pip install openpyxl
python excel_a_json.py MiArchivoNuevo.xlsx
git add arbol.json && git commit -m "Actualiza datos" && git push
```

**Solo en tu navegador.** En la pestaña *Datos a ingresar*, sube el Excel y pulsa *Guardar árbol*. Se guarda en ese navegador (localStorage) y nadie más lo ve. Para volver a los datos del repositorio, usa *Vaciar árbol* y recarga la página.

## Formato del Excel

La primera fila lleva los nombres de las columnas y cada fila siguiente es un código.

| categoria | subcategoria | producto | sku | marca | modalidad | precio | inventario | costo | venta_mes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Plomería | Válvulas de bola | Llave de bola PVC 1/2" roscar | 22-70-165 | Pavco | Autoservicio con apoyo | 3,20 | 1200 | 2,10 | 340 |

- **Obligatorias:** las columnas de nivel. Pueden ser más o menos de tres.
- **Opcionales:** código, marca, modalidad (Autoservicio con apoyo, Venta asistida…), precio, inventario, costo y venta por mes. Si vienen, aparecen en los indicadores y las tablas. El inventario valorado se calcula como inventario × costo, o inventario × precio si no hay costo.
- La página detecta cada columna por su nombre. Al subir el archivo desde la página puedes cambiar a mano qué hace cada una.

## Probar en tu computadora

Con Streamlit: `pip install -r requirements.txt` y luego `streamlit run streamlit_app.py`.

Sin Streamlit: al abrir `index.html` con doble clic, el navegador no deja leer `arbol.json`, así que la página arranca vacía. Para verla con los datos, levanta un servidor local en esta carpeta:

```bash
python -m http.server 8000
```

Luego abre `http://localhost:8000`.
