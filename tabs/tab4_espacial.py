"""
Tab 4: Análisis Espacial por Sitio de Muestreo
"""

import pandas as pd
import streamlit as st
import plotly.express as px


def render(composition_data, diversity_data):
    st.header("🗺️ Análisis Espacial por Sitio de Muestreo")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(diversity_data.keys()), key='spatial_dataset'
    )
    df_div = diversity_data[dataset_choice]
    df_comp = composition_data[dataset_choice]

    subtab1, subtab2 = st.tabs(["Gradientes longitudinales", "Composición por sitio"])

    with subtab1:
        st.subheader("Gradientes de Diversidad a lo Largo del Río")

        df_div['Site_num'] = pd.to_numeric(df_div['Site'], errors='coerce')
        df_plot = df_div.dropna(subset=['Site_num']).sort_values('Site_num')

        metric_choice = st.selectbox(
            "Selecciona métrica:", ['Shannon', 'Simpson', 'Pielou', 'Richness'], key='spatial_metric'
        )

        fig = px.scatter(
            df_plot,
            x='Site_num', y=metric_choice,
            color='Type',
            color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
            symbol='Type',
            title=f'{metric_choice} por Sitio de Muestreo',
            labels={'Site_num': 'Sitio', metric_choice: metric_choice},
            trendline='lowess'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        st.subheader("Composición Taxonómica por Sitio")

        df_comp_site = df_comp.copy()
        df_comp_site['Site'] = df_comp_site.index.str.extract(r'(\d+)')[0]
        df_comp_site['Type'] = ['SED' if 'SED' in s else 'PLA' for s in df_comp_site.index]

        sites = sorted(df_comp_site['Site'].unique())
        site_choice = st.selectbox("Selecciona sitio:", sites, key='site_select')

        df_site = df_comp_site[df_comp_site['Site'] == site_choice]
        phylum_cols = [col for col in df_site.columns if col not in ['Site', 'Type']]
        df_site_rel = df_site[phylum_cols].div(df_site[phylum_cols].sum(axis=1), axis=0)
        df_site_rel['Type'] = df_site['Type'].values
        df_site_rel['Sample'] = df_site.index

        df_melt = df_site_rel.melt(id_vars=['Sample', 'Type'], var_name='Phylum', value_name='Abundance')

        fig = px.bar(
            df_melt, x='Sample', y='Abundance', color='Phylum',
            title=f'Composición en Sitio {site_choice}',
            labels={'Abundance': 'Abundancia Relativa'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(barmode='stack', height=500)
        st.plotly_chart(fig, use_container_width=True)
