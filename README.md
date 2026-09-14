# Dashboard Inmuebles CISA

## Contenido
- `app.py` — código Streamlit del dashboard
- `requirements.txt` — dependencias
- `Inmuebles_CISA.xlsx` — base de datos

## Ejecutar en local
```bash
pip install -r requirements.txt
streamlit run app.py
```
Se abrirá en `http://localhost:8501`.

## Publicar una URL pública gratis (Streamlit Community Cloud)
1. Crea un repositorio en GitHub y sube estos 3 archivos (`app.py`, `requirements.txt`, `Inmuebles_CISA.xlsx`).
2. Entra a https://share.streamlit.io con tu cuenta de GitHub.
3. Click en "New app" → selecciona el repo, la rama y `app.py` como archivo principal.
4. Click en "Deploy". En 1-2 minutos obtendrás una URL pública tipo:
   `https://tu-usuario-inmuebles-cisa.streamlit.app`

No puedo generar esa URL yo mismo porque el despliegue requiere tu cuenta de GitHub/Streamlit; el proceso de arriba toma menos de 5 minutos.
