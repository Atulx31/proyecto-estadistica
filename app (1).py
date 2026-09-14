"""
Dashboard Interactivo - Inmuebles CISA
Autor: Analista de Datos (Python/Streamlit)
Descripción: Cuadro de mando con filtro por Departamento que actualiza
             dinámicamente 5 visualizaciones sobre el portafolio de inmuebles.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Inmuebles CISA",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_COLOR = "#1f4e79"
PALETTE = px.colors.sequential.Blues_r

# ------------------------------------------------------------------
# CARGA DE DATOS (con caché para performance)
# ------------------------------------------------------------------
@st.cache_data
def cargar_datos(ruta: str) -> pd.DataFrame:
    df = pd.read_excel(ruta, sheet_name="Hoja1")
    # Normalización básica de texto por si hay espacios extra
    for col in ["Ciudad", "Departamento", "Orientacion", "Tipo_Inmueble", "Estado_Inmueble"]:
        df[col] = df[col].astype(str).str.strip()
    return df


# Ruta absoluta basada en la ubicación de este script, para que funcione
# sin importar desde qué directorio de trabajo lo ejecute Streamlit Cloud.
DIRECTORIO_APP = os.path.dirname(os.path.abspath(__file__))
RUTA_ARCHIVO = os.path.join(DIRECTORIO_APP, "Inmuebles_CISA.xlsx")

if not os.path.exists(RUTA_ARCHIVO):
    st.error(
        f"❌ No se encontró el archivo **Inmuebles_CISA.xlsx** en el repositorio.\n\n"
        f"Ruta esperada: `{RUTA_ARCHIVO}`\n\n"
        f"Archivos presentes en la carpeta de la app:\n\n"
        + "\n".join(f"- {f}" for f in sorted(os.listdir(DIRECTORIO_APP)))
        + "\n\nVerifica que el archivo esté subido en la raíz del repositorio de "
        "GitHub, con ese nombre exacto (mayúsculas incluidas)."
    )
    st.stop()

df = cargar_datos(RUTA_ARCHIVO)

# ------------------------------------------------------------------
# BARRA LATERAL - FILTROS
# ------------------------------------------------------------------
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/1040/1040993.png", width=70
)
st.sidebar.title("Filtros")

departamentos = sorted(df["Departamento"].unique().tolist())
opciones_depto = ["Todos"] + departamentos

depto_seleccionado = st.sidebar.selectbox(
    "Selecciona un Departamento:",
    options=opciones_depto,
    index=0,
)

# Aplicar filtro dinámico
if depto_seleccionado == "Todos":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df["Departamento"] == depto_seleccionado].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Inmuebles filtrados", f"{len(df_filtrado):,}")
st.sidebar.metric(
    "Precio promedio (MM)",
    f"${df_filtrado['Precio_VTA_MM'].mean():,.2f}" if len(df_filtrado) else "N/A",
)
st.sidebar.metric(
    "Precio total (MM)",
    f"${df_filtrado['Precio_VTA_MM'].sum():,.2f}" if len(df_filtrado) else "N/A",
)

st.sidebar.markdown("---")
st.sidebar.caption("Fuente: Inmuebles_CISA.xlsx")

# ------------------------------------------------------------------
# ENCABEZADO
# ------------------------------------------------------------------
st.title("🏢 Dashboard Interactivo de Inmuebles - CISA")
st.markdown(
    f"**Departamento seleccionado:** `{depto_seleccionado}` &nbsp;|&nbsp; "
    f"**Total de registros:** `{len(df_filtrado)}`"
)
st.markdown("---")

if df_filtrado.empty:
    st.warning("No hay registros para el departamento seleccionado.")
    st.stop()

# ------------------------------------------------------------------
# FILA 1: Ciudad (barras) + Orientación (pastel)
# ------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Distribución de Inmuebles por Ciudad")
    conteo_ciudad = (
        df_filtrado["Ciudad"]
        .value_counts()
        .reset_index()
    )
    conteo_ciudad.columns = ["Ciudad", "Cantidad"]
    conteo_ciudad = conteo_ciudad.sort_values("Cantidad", ascending=True)

    fig_ciudad = px.bar(
        conteo_ciudad,
        x="Cantidad",
        y="Ciudad",
        orientation="h",
        text="Cantidad",
        color="Cantidad",
        color_continuous_scale=PALETTE,
    )
    fig_ciudad.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=max(350, 22 * len(conteo_ciudad)),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_ciudad, use_container_width=True)

with col2:
    st.subheader("2️⃣ Distribución por Orientación de Uso")
    conteo_orient = df_filtrado["Orientacion"].value_counts().reset_index()
    conteo_orient.columns = ["Orientacion", "Cantidad"]

    fig_orient = px.pie(
        conteo_orient,
        names="Orientacion",
        values="Cantidad",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_orient.update_traces(textinfo="percent+label")
    fig_orient.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=400)
    st.plotly_chart(fig_orient, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------
# FILA 2: Histograma de Precio de Venta
# ------------------------------------------------------------------
st.subheader("3️⃣ Histograma de Frecuencias - Precio de Venta (MM)")

precios = df_filtrado["Precio_VTA_MM"].dropna()
n_bins = min(12, max(1, precios.nunique()))

fig_hist = px.histogram(
    df_filtrado,
    x="Precio_VTA_MM",
    nbins=n_bins,
    color_discrete_sequence=[PRIMARY_COLOR],
)
fig_hist.update_layout(
    bargap=0.05,
    xaxis_title="Precio de Venta (MM $)",
    yaxis_title="Frecuencia (N.° de inmuebles)",
    height=420,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_hist, use_container_width=True)

with st.expander("Ver estadísticas descriptivas del precio de venta"):
    st.dataframe(
        precios.describe().rename("Precio_VTA_MM (MM $)").to_frame(),
        use_container_width=True,
    )

st.markdown("---")

# ------------------------------------------------------------------
# FILA 3: Tipo de Inmueble (barras horizontales) + Estado (pastel)
# ------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("4️⃣ Distribución por Tipo de Inmueble")
    conteo_tipo = df_filtrado["Tipo_Inmueble"].value_counts().reset_index()
    conteo_tipo.columns = ["Tipo_Inmueble", "Cantidad"]
    conteo_tipo = conteo_tipo.sort_values("Cantidad", ascending=True)

    fig_tipo = px.bar(
        conteo_tipo,
        x="Cantidad",
        y="Tipo_Inmueble",
        orientation="h",
        text="Cantidad",
        color="Cantidad",
        color_continuous_scale=PALETTE,
    )
    fig_tipo.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=max(350, 28 * len(conteo_tipo)),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_tipo, use_container_width=True)

with col4:
    st.subheader("5️⃣ Distribución del Estado de los Inmuebles")
    conteo_estado = df_filtrado["Estado_Inmueble"].value_counts().reset_index()
    conteo_estado.columns = ["Estado_Inmueble", "Cantidad"]
    # Orden lógico según el prefijo numérico del estado
    conteo_estado = conteo_estado.sort_values("Estado_Inmueble")

    fig_estado = px.pie(
        conteo_estado,
        names="Estado_Inmueble",
        values="Cantidad",
        hole=0.0,
        color_discrete_sequence=px.colors.diverging.RdYlGn,
    )
    fig_estado.update_traces(textinfo="percent+label")
    fig_estado.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=430)
    st.plotly_chart(fig_estado, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------
# TABLA DE DATOS DETALLE (opcional, colapsable)
# ------------------------------------------------------------------
with st.expander("📋 Ver datos detallados"):
    st.dataframe(df_filtrado, use_container_width=True)
    csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"inmuebles_{depto_seleccionado}.csv",
        mime="text/csv",
    )

st.caption("Dashboard construido con Streamlit + Plotly • Datos: Inmuebles_CISA.xlsx")
