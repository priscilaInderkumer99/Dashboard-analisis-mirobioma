"""
Tab 4: Análisis Espacial por Sitio de Muestreo
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import re

def render(composition_data, diversity_data, metadata_dict=None):
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
            "Selecciona métrica:", 
            ['Shannon', 'Simpson', 'Pielou', 'Richness'], 
            key='spatial_metric'
        )
        
        fig = px.scatter(
            df_plot,
            x='Site_num', 
            y=metric_choice,
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
        
        # Extraer sitio de manera más robusta
        def extract_site(sample_name):
            """Extrae el número de sitio de nombres como E_1PLA, E_10SED, 1PLA, 8SED"""
            # Remover prefijo E_ si existe
            clean = sample_name.replace('E_', '')
            # Extraer todos los dígitos iniciales
            match = re.match(r'(\d+)', clean)
            return match.group(1) if match else None
        
        df_comp_site['Site'] = df_comp_site.index.map(extract_site)
        df_comp_site['Type'] = ['SED' if 'SED' in s else 'PLA' for s in df_comp_site.index]
        
        # Filtrar sitios válidos
        df_comp_site = df_comp_site[df_comp_site['Site'].notna()]
        
        if len(df_comp_site) == 0:
            st.warning("⚠️ No se pudieron extraer sitios de los nombres de muestra")
            st.info(f"Muestras disponibles: {df_comp.index.tolist()[:5]}...")
        else:
            # Ordenar sitios numéricamente
            sites = sorted(df_comp_site['Site'].unique(), key=lambda x: int(x))
            site_choice = st.selectbox("Selecciona sitio:", sites, key='site_select')
            
            df_site = df_comp_site[df_comp_site['Site'] == site_choice]
            
            phylum_cols = [col for col in df_site.columns if col not in ['Site', 'Type']]
            df_site_rel = df_site[phylum_cols].div(df_site[phylum_cols].sum(axis=1), axis=0)
            df_site_rel['Type'] = df_site['Type'].values
            df_site_rel['Sample'] = df_site.index
            
            df_melt = df_site_rel.melt(
                id_vars=['Sample', 'Type'], 
                var_name='Phylum', 
                value_name='Abundance'
            )
            
            # Generar suficientes colores
            n_phylums = df_melt['Phylum'].nunique()
            palette = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Safe
            colors = [palette[i % len(palette)] for i in range(n_phylums)]
            
            fig = px.bar(
                df_melt, 
                x='Sample', 
                y='Abundance', 
                color='Phylum',
                title=f'Composición en Sitio {site_choice}',
                labels={'Abundance': 'Abundancia Relativa'},
                color_discrete_sequence=colors
            )
            fig.update_layout(barmode='stack', height=500)
            st.plotly_chart(fig, use_container_width=True)
