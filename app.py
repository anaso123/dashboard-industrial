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
# ---------------------------
# NAVEGACIÓN
# ---------------------------
seccion = st.sidebar.radio(
    "Selecciona una sección",
    [
        "Producción y calidad",
        "Variables operativas",
        "Análisis de fallas",
        "Datos",
        "Hallazgos y recomendaciones"
    ]
)

# ---------------------------
# PRODUCCIÓN Y CALIDAD
# ---------------------------
if seccion == "Producción y calidad":

    st.header("Producción y calidad")

    produccion_linea = (
        df_filtrado.groupby("linea", as_index=False)["produccion"]
        .sum()
    )

    fig_produccion_linea = px.bar(
        produccion_linea,
        x="linea",
        y="produccion",
        color="linea",
        title="Producción acumulada por línea",
        text_auto=True
    )

    st.plotly_chart(
        fig_produccion_linea,
        use_container_width=True
    )

    produccion_fecha = (
        df_filtrado.groupby("fecha", as_index=False)["produccion"]
        .sum()
    )

    fig_produccion_fecha = px.line(
        produccion_fecha,
        x="fecha",
        y="produccion",
        markers=True,
        title="Evolución diaria de la producción"
    )

    st.plotly_chart(
        fig_produccion_fecha,
        use_container_width=True
    )

    produccion_turno = (
        df_filtrado.groupby("turno", as_index=False)["produccion"]
        .sum()
    )

    fig_produccion_turno = px.bar(
        produccion_turno,
        x="turno",
        y="produccion",
        color="turno",
        title="Producción acumulada por turno",
        text_auto=True
    )

    st.plotly_chart(
        fig_produccion_turno,
        use_container_width=True
    )

    calidad_linea = (
        df_filtrado.groupby("linea", as_index=False)
        .agg(
            produccion=("produccion", "sum"),
            defectos=("defectos", "sum")
        )
    )

    calidad_linea["porcentaje_defectos"] = (
        calidad_linea["defectos"]
        / calidad_linea["produccion"]
        * 100
    ).round(2)

    col_grafica1, col_grafica2 = st.columns(2)

    fig_defectos_linea = px.bar(
        calidad_linea,
        x="linea",
        y="defectos",
        color="linea",
        title="Defectos por línea",
        text_auto=True
    )

    col_grafica1.plotly_chart(
        fig_defectos_linea,
        use_container_width=True
    )

    fig_porcentaje_defectos = px.bar(
        calidad_linea,
        x="linea",
        y="porcentaje_defectos",
        color="linea",
        title="Porcentaje de defectos por línea",
        text_auto=".2f"
    )

    col_grafica2.plotly_chart(
        fig_porcentaje_defectos,
        use_container_width=True
    )

    defectos_turno = (
        df_filtrado.groupby("turno", as_index=False)["defectos"]
        .sum()
    )

    "Datos"
        defectos_turno,
        x="turno",
        y="defectos",
        color="turno",
        title="Defectos por turno",
        text_auto=True
    )
        st.plotly_chart(
        fig_defectos_turno,
        use_container_width=True
    )
    # ---------------------------
# VARIABLES OPERATIVAS
# ---------------------------
elif seccion == "Variables operativas":

    st.header("Variables operativas")

    variables_hora = (
        df_filtrado
        .set_index("timestamp")
        .groupby("linea")[
            ["temperatura", "vibracion", "presion"]
        ]
        .resample("1h")
        .mean()
        .reset_index()
    )

    fig_temperatura = px.line(
        variables_hora,
        x="timestamp",
        y="temperatura",
        color="linea",
        title="Evolución de la temperatura por línea"
    )

    st.plotly_chart(
        fig_temperatura,
        use_container_width=True
    )

    fig_vibracion = px.line(
        variables_hora,
        x="timestamp",
        y="vibracion",
        color="linea",
        title="Evolución de la vibración por línea"
    )

    st.plotly_chart(
        fig_vibracion,
        use_container_width=True
    )

    fig_presion = px.line(
        variables_hora,
        x="timestamp",
        y="presion",
        color="linea",
        title="Evolución de la presión por línea"
    )

    st.plotly_chart(
        fig_presion,
        use_container_width=True
    )

  # ---------------------------
# ANÁLISIS DE FALLAS
# ---------------------------
elif seccion == "Análisis de fallas":

    st.header("Análisis de fallas")

    fallas_linea = (
        df_filtrado.groupby("linea", as_index=False)
        .agg(
            total_registros=("falla", "count"),
            registros_con_falla=("falla", "sum")
        )
    )

    fallas_linea["porcentaje_fallas"] = (
        fallas_linea["registros_con_falla"]
        / fallas_linea["total_registros"]
        * 100
    ).round(2)

    col_falla1, col_falla2 = st.columns(2)

    fig_fallas_linea = px.bar(
        fallas_linea,
        x="linea",
        y="registros_con_falla",
        color="linea",
        title="Registros con falla por línea",
        text_auto=True
    )

    col_falla1.plotly_chart(
        fig_fallas_linea,
        use_container_width=True
    )

    fig_porcentaje_fallas = px.bar(
        fallas_linea,
        x="linea",
        y="porcentaje_fallas",
        color="linea",
        title="Porcentaje de fallas por línea",
        text_auto=".2f"
    )

    col_falla2.plotly_chart(
        fig_porcentaje_fallas,
        use_container_width=True
    )

    fallas_fecha = (
        df_filtrado.groupby("fecha", as_index=False)["falla"]
        .sum()
    )

    fig_fallas_fecha = px.line(
        fallas_fecha,
        x="fecha",
        y="falla",
        markers=True,
        title="Evolución diaria de las fallas"
    )

    st.plotly_chart(
        fig_fallas_fecha,
        use_container_width=True
    )

    relacion_falla = df_filtrado.copy()

    relacion_falla["estado"] = relacion_falla["falla"].map({
        0: "Sin falla",
        1: "Con falla"
    })

    fig_relacion = px.box(
        relacion_falla,
        x="estado",
        y="vibracion",
        color="estado",
        title="Relación entre vibración y presencia de falla"
    )

    st.plotly_chart(
        fig_relacion,
        use_container_width=True
    )
# ---------------------------
# DATOS Y DESCARGA
# ---------------------------
elif seccion == "Datos":

    st.header("Datos filtrados")

    st.dataframe(
        df_filtrado,
        use_container_width=True
    )

    csv = df_filtrado.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Descargar datos filtrados en CSV",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )
