"""
Tab 1: Análisis de Composición de Comunidades
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render(composition_data):
    st.header("📊 Análisis de Composición de Comunidades")

    dataset_choice = st.selectbox("Selecciona dataset:", list(composition_data.keys()))
    df_comp = composition_data[dataset_choice]

    subtab1, subtab2, subtab3 = st.tabs(["Barras apiladas", "Heatmap", "Tabla"])

    with subtab1:
        st.subheader("Perfiles de Comunidad por Muestra")

        sample_filter = st.radio(
            "Filtrar por tipo:",
            ["Todos", "Solo Sedimento (SED)", "Solo Plancton (PLA)"],
            horizontal=True
        )

        if sample_filter == "Solo Sedimento (SED)":
            samples_to_plot = [s for s in df_comp.index if 'SED' in s]
        elif sample_filter == "Solo Plancton (PLA)":
            samples_to_plot = [s for s in df_comp.index if 'PLA' in s]
        else:
            samples_to_plot = df_comp.index.tolist()

        df_plot = df_comp.loc[samples_to_plot]
        df_relative = df_plot.div(df_plot.sum(axis=1), axis=0).fillna(0)

        fig = go.Figure()
        colors = px.colors.qualitative.Set3[:len(df_relative.columns)]

        for idx, phylum in enumerate(df_relative.columns):
            fig.add_trace(go.Bar(
                name=phylum,
                x=df_relative.index,
                y=df_relative[phylum],
                marker_color=colors[idx]
            ))

        fig.update_layout(
            barmode='stack',
            title=f'Composición de Comunidades - {dataset_choice}',
            xaxis_title='Muestra',
            yaxis_title='Abundancia Relativa',
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        st.subheader("Heatmap de Abundancia Relativa")
        df_relative = df_comp.div(df_comp.sum(axis=1), axis=0).fillna(0)

        fig = px.imshow(
            df_relative.T,
            labels=dict(x="Muestra", y="Phylum", color="Abundancia Relativa"),
            x=df_relative.index,
            y=df_relative.columns,
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig.update_layout(title=f'Heatmap de Composición - {dataset_choice}', height=600)
        st.plotly_chart(fig, use_container_width=True)

    with subtab3:
        st.subheader("Tabla de Abundancias")
        st.dataframe(df_comp, use_container_width=True)

        csv = df_comp.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Descargar tabla (CSV)",
            data=csv,
            file_name=f'composition_{dataset_choice}.csv',
            mime='text/csv',
        )
