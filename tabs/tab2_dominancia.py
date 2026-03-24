"""
Tab 2: Análisis de Dominancia
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render(composition_data, diversity_data):
    st.header("👑 Análisis de Dominancia")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(diversity_data.keys()), key='dom_dataset'
    )
    df_div = diversity_data[dataset_choice]

    subtab1, subtab2, subtab3 = st.tabs(["Índices", "Curvas rango-abundancia", "Core vs Raros"])

    with subtab1:
        st.subheader("Índices de Dominancia y Equitatividad")

        col1, col2, col3 = st.columns(3)
        for col, metric, title in zip(
            [col1, col2, col3],
            ['Simpson', 'Pielou', 'Richness'],
            ['Índice de Simpson', 'Equitatividad de Pielou', 'Riqueza de Phylums']
        ):
            with col:
                fig = px.box(
                    df_div, x='Type', y=metric, color='Type',
                    color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                    points='all', title=title
                )
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Estadísticas descriptivas")
        summary = df_div.groupby('Type')[['Simpson', 'Pielou', 'Richness', 'Shannon']].agg(['mean', 'std'])
        st.dataframe(summary)

    with subtab2:
        st.subheader("Curvas de Rango-Abundancia")

        df_comp = composition_data[dataset_choice]
        sample_select = st.selectbox("Selecciona muestra:", df_comp.index.tolist(), key='rank_sample')

        abundances = df_comp.loc[sample_select].sort_values(ascending=False)
        abundances = abundances[abundances > 0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(abundances) + 1)),
            y=abundances.values,
            mode='lines+markers',
            name='Abundancia',
            text=abundances.index,
            hovertemplate='<b>%{text}</b><br>Rank: %{x}<br>Abundancia: %{y}<extra></extra>'
        ))
        fig.update_layout(
            title=f'Curva Rango-Abundancia - {sample_select}',
            xaxis_title='Rango',
            yaxis_title='Abundancia (lecturas)',
            yaxis_type='log',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    with subtab3:
        st.subheader("Análisis Core vs Raros")

        df_comp = composition_data[dataset_choice]
        presence = (df_comp > 0).sum(axis=0) / len(df_comp) * 100

        core_phylums = presence[presence >= 80].index.tolist()
        rare_phylums = presence[presence <= 20].index.tolist()
        intermediate_phylums = presence[(presence > 20) & (presence < 80)].index.tolist()

        col1, col2, col3 = st.columns(3)
        for col, label, phylums in zip(
            [col1, col2, col3],
            ["Core Phylums (≥80%)", "Intermedios (20-80%)", "Raros (≤20%)"],
            [core_phylums, intermediate_phylums, rare_phylums]
        ):
            with col:
                st.metric(label, len(phylums))
                if phylums:
                    st.write(phylums)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=presence.index,
            y=presence.values,
            marker_color=['green' if p >= 80 else 'orange' if p > 20 else 'red' for p in presence.values]
        ))
        fig.update_layout(
            title='Frecuencia de Presencia de Phylums',
            xaxis_title='Phylum',
            yaxis_title='% de muestras',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
