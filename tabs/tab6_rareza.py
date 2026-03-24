"""
Tab 6: Rareza y Taxa Únicos
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render(composition_data):
    st.header("💎 Análisis de Rareza y Taxa Únicos")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(composition_data.keys()), key='rare_dataset'
    )
    df_comp = composition_data[dataset_choice]

    subtab1, subtab2 = st.tabs(["Taxa únicos SED vs PLA", "Proporción de raros"])

    with subtab1:
        st.subheader("Phylums Únicos y Compartidos")

        sed_samples = [s for s in df_comp.index if 'SED' in s]
        pla_samples = [s for s in df_comp.index if 'PLA' in s]

        sed_phylums = set(df_comp.loc[sed_samples].columns[(df_comp.loc[sed_samples] > 0).any()])
        pla_phylums = set(df_comp.loc[pla_samples].columns[(df_comp.loc[pla_samples] > 0).any()])

        shared = sed_phylums & pla_phylums
        sed_unique = sed_phylums - pla_phylums
        pla_unique = pla_phylums - sed_phylums

        col1, col2, col3 = st.columns(3)
        for col, label, items in zip(
            [col1, col2, col3],
            ["Únicos Sedimento", "Compartidos", "Únicos Plancton"],
            [sed_unique, shared, pla_unique]
        ):
            with col:
                st.metric(label, len(items))
                if items:
                    if label == "Compartidos":
                        with st.expander("Ver listado"):
                            st.write(list(items))
                    else:
                        st.write(list(items))

        st.info(f"""
        - **Total phylums en Sedimento**: {len(sed_phylums)}
        - **Total phylums en Plancton**: {len(pla_phylums)}
        - **Phylums compartidos**: {len(shared)} ({len(shared)/max(len(sed_phylums), len(pla_phylums))*100:.1f}%)
        """)

    with subtab2:
        st.subheader("Proporción de Phylums Raros")

        threshold = st.slider(
            "Umbral de abundancia relativa para considerar 'raro' (%):",
            min_value=0.1, max_value=5.0, value=1.0, step=0.1
        )

        df_relative = df_comp.div(df_comp.sum(axis=1), axis=0).fillna(0) * 100
        rare_counts = (df_relative < threshold).sum(axis=1)
        total_counts = (df_relative > 0).sum(axis=1)
        rare_proportion = rare_counts / total_counts * 100

        import pandas as pd
        df_rare = pd.DataFrame({
            'Sample': df_comp.index,
            'Rare_proportion': rare_proportion,
            'Type': ['SED' if 'SED' in s else 'PLA' for s in df_comp.index]
        })

        fig = px.box(
            df_rare, x='Type', y='Rare_proportion', color='Type',
            color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
            points='all',
            title=f'Proporción de Phylums Raros (< {threshold}% abundancia relativa)',
            labels={'Rare_proportion': '% de phylums raros'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
