"""
Tab 7: Ratios entre Phylums
"""

import streamlit as st
import plotly.express as px
from scipy import stats
from scipy.stats import mannwhitneyu
import pandas as pd


def render(composition_data):
    st.header("📐 Análisis de Ratios entre Phylums")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(composition_data.keys()), key='ratio_dataset'
    )
    df_comp = composition_data[dataset_choice]
    phylums = df_comp.columns.tolist()

    subtab1, subtab2 = st.tabs(["Ratios personalizados", "Scatter plots"])

    with subtab1:
        st.subheader("Calcular Ratio entre Phylums")

        col1, col2 = st.columns(2)
        with col1:
            phylum1 = st.selectbox("Numerador:", phylums, key='p1')
        with col2:
            phylum2 = st.selectbox("Denominador:", phylums, key='p2', index=min(1, len(phylums) - 1))

        if phylum1 and phylum2:
            ratio = df_comp[phylum1] / (df_comp[phylum2] + 1)
            df_ratio = pd.DataFrame({
                'Sample': df_comp.index,
                'Ratio': ratio,
                'Type': ['SED' if 'SED' in s else 'PLA' for s in df_comp.index]
            })

            fig = px.box(
                df_ratio, x='Type', y='Ratio', color='Type',
                color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                points='all', title=f'Ratio {phylum1} / {phylum2}',
                labels={'Ratio': f'{phylum1}/{phylum2}'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            sed_ratio = df_ratio[df_ratio['Type'] == 'SED']['Ratio']
            pla_ratio = df_ratio[df_ratio['Type'] == 'PLA']['Ratio']

            if len(sed_ratio) > 1 and len(pla_ratio) > 1:
                stat, pval = mannwhitneyu(sed_ratio, pla_ratio)
                st.info(f"""
                **Test de Mann-Whitney U:**
                - Media SED: {sed_ratio.mean():.3f}
                - Media PLA: {pla_ratio.mean():.3f}
                - p-value: {pval:.4f}
                - Significativo: {'Sí' if pval < 0.05 else 'No'}
                """)

    with subtab2:
        st.subheader("Correlación entre Phylums")

        col1, col2 = st.columns(2)
        with col1:
            phylum_x = st.selectbox("Eje X:", phylums, key='px')
        with col2:
            phylum_y = st.selectbox("Eje Y:", phylums, key='py', index=min(1, len(phylums) - 1))

        if phylum_x and phylum_y:
            df_scatter = pd.DataFrame({
                'X': df_comp[phylum_x],
                'Y': df_comp[phylum_y],
                'Sample': df_comp.index,
                'Type': ['SED' if 'SED' in s else 'PLA' for s in df_comp.index]
            })

            fig = px.scatter(
                df_scatter, x='X', y='Y', color='Type',
                color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                symbol='Type', text='Sample',
                title=f'Correlación: {phylum_x} vs {phylum_y}',
                labels={'X': f'{phylum_x} (lecturas)', 'Y': f'{phylum_y} (lecturas)'},
                trendline='ols'
            )
            fig.update_traces(textposition='top center', textfont_size=8)
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            corr, pval = stats.spearmanr(df_scatter['X'], df_scatter['Y'])
            st.info(f"""
            **Correlación de Spearman:**
            - Coeficiente: {corr:.3f}
            - p-value: {pval:.4f}
            - Interpretación: {'Correlación significativa' if pval < 0.05 else 'Sin correlación significativa'}
            """)
