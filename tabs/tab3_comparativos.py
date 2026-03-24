"""
Tab 3: Análisis Comparativos (SED vs PLA)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import mannwhitneyu


def render(diversity_data):
    st.header("⚖️ Análisis Comparativos: Sedimento vs Plancton")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(diversity_data.keys()), key='comp_dataset'
    )
    df_div = diversity_data[dataset_choice]

    subtab1, subtab2 = st.tabs(["Diversidad Alfa", "Tests Estadísticos"])

    with subtab1:
        st.subheader("Comparación de Métricas de Diversidad")

        metrics = ['Shannon', 'Simpson', 'Pielou', 'Richness']
        fig = make_subplots(rows=2, cols=2, subplot_titles=metrics)

        for idx, metric in enumerate(metrics):
            row, col = idx // 2 + 1, idx % 2 + 1
            sed_data = df_div[df_div['Type'] == 'SED'][metric]
            pla_data = df_div[df_div['Type'] == 'PLA'][metric]

            fig.add_trace(
                go.Box(y=sed_data, name='SED', marker_color='chocolate', showlegend=(idx == 0)),
                row=row, col=col
            )
            fig.add_trace(
                go.Box(y=pla_data, name='PLA', marker_color='steelblue', showlegend=(idx == 0)),
                row=row, col=col
            )

        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        st.subheader("Tests de Mann-Whitney U")

        results = []
        for metric in ['Shannon', 'Simpson', 'Pielou', 'Richness']:
            sed_data = df_div[df_div['Type'] == 'SED'][metric]
            pla_data = df_div[df_div['Type'] == 'PLA'][metric]

            if len(sed_data) > 1 and len(pla_data) > 1:
                stat, pval = mannwhitneyu(sed_data, pla_data)
                sig = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else 'ns'
                results.append({
                    'Métrica': metric,
                    'Media SED': f"{sed_data.mean():.3f}",
                    'Media PLA': f"{pla_data.mean():.3f}",
                    'U-statistic': f"{stat:.2f}",
                    'p-value': f"{pval:.4f}",
                    'Significancia': sig
                })

        import pandas as pd
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        st.info("**Significancia:** ns: p>0.05 | *: p<0.05 | **: p<0.01 | ***: p<0.001")
