"""
Tab 8: Comparación 16S vs 18S
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def render(composition_data, diversity_data):
    st.header("🔬 Comparación 16S (Procariotas) vs 18S (Eucariotas)")

    if '16S' not in diversity_data or '18S' not in diversity_data:
        st.warning("Se necesitan datos de ambos datasets (16S y 18S) para esta comparación")
        return

    subtab1, subtab2 = st.tabs(["Métricas comparadas", "Composición lado a lado"])

    with subtab1:
        st.subheader("Comparación de Métricas de Diversidad")

        df_16s = diversity_data['16S'].copy()
        df_16s['Dataset'] = '16S (Procariotas)'
        df_18s = diversity_data['18S'].copy()
        df_18s['Dataset'] = '18S (Eucariotas)'
        df_combined = pd.concat([df_16s, df_18s])

        for metric in ['Shannon', 'Simpson', 'Pielou', 'Richness']:
            fig = px.box(
                df_combined, x='Dataset', y=metric, color='Type',
                color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                points='all',
                title=f'Comparación de {metric}: 16S vs 18S'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        st.subheader("Riqueza de Phylums: 16S vs 18S")

        n_phylums_16s = composition_data['16S'].shape[1]
        n_phylums_18s = composition_data['18S'].shape[1]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Phylums detectados 16S", n_phylums_16s)
            st.write("**Phylums 16S:**")
            st.write(composition_data['16S'].columns.tolist())

        with col2:
            st.metric("Phylums detectados 18S", n_phylums_18s)
            st.write("**Phylums 18S:**")
            st.write(composition_data['18S'].columns.tolist())
