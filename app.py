import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(
    page_title="Dashboard Industrial",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Dashboard de Monitoreo Industrial")
st.write(
    "Análisis de producción, calidad, variables operativas y fallas."
)

# ---------------------------
# CARGA DE DATOS
# ---------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/dataset_planta_bigdata.csv")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["fecha"] = df["timestamp"].dt.date

    return df


df = cargar_datos()

# ---------------------------
# FILTROS
# ---------------------------
st.sidebar.header("Filtros")

lineas_disponibles = sorted(df["linea"].unique())

lineas_seleccionadas = st.sidebar.multiselect(
    "Línea de producción",
    options=lineas_disponibles,
    default=lineas_disponibles
)

turnos_disponibles = sorted(df["turno"].unique())

turnos_seleccionados = st.sidebar.multiselect(
    "Turno",
    options=turnos_disponibles,
    default=turnos_disponibles
)

fecha_inicial = df["fecha"].min()
fecha_final = df["fecha"].max()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_inicial, fecha_final),
    min_value=fecha_inicial,
    max_value=fecha_final
)

# ---------------------------
# DATOS FILTRADOS
# ---------------------------
if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
    inicio, fin = rango_fechas
else:
    inicio = fecha_inicial
    fin = fecha_final

df_filtrado = df[
    (df["linea"].isin(lineas_seleccionadas))
    & (df["turno"].isin(turnos_seleccionados))
    & (df["fecha"] >= inicio)
    & (df["fecha"] <= fin)
].copy()

# ---------------------------
# INDICADORES KPI
# ---------------------------
if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

produccion_total = df_filtrado["produccion"].sum()
produccion_promedio = df_filtrado["produccion"].mean()
defectos_totales = df_filtrado["defectos"].sum()

porcentaje_defectos = (
    defectos_totales / produccion_total * 100
    if produccion_total > 0
    else 0
)

registros_con_falla = df_filtrado["falla"].sum()

porcentaje_fallas = (
    registros_con_falla / len(df_filtrado) * 100
    if len(df_filtrado) > 0
    else 0
)

st.subheader("Resumen general")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Producción total",
    f"{produccion_total:,.0f}"
)

col2.metric(
    "Producción promedio",
    f"{produccion_promedio:.2f}"
)

col3.metric(
    "Defectos totales",
    f"{defectos_totales:,.0f}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Porcentaje de defectos",
    f"{porcentaje_defectos:.2f}%"
)

col5.metric(
    "Registros con falla",
    f"{registros_con_falla:,.0f}"
)

col6.metric(
    "Porcentaje de fallas",
    f"{porcentaje_fallas:.2f}%"
)
