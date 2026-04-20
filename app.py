"""
=============================================================================
DASHBOARD DE ANÁLISIS DE MICROBIOMAS - 16S y 18S
=============================================================================
Autor: Priscila Inderkumer
Fecha: 2026
Descripción: Dashboard interactivo para análisis de comunidades microbianas
             de sedimento y plancton usando datos de metabarcoding
=============================================================================
"""

import warnings
warnings.filterwarnings('ignore')

import streamlit as st

from utils.data_loader import (
    load_and_process_otus,
    load_feature_table_with_taxonomy,
    load_metadata,
    create_composition_matrix,
    merge_with_metadata,
)
from utils.diversity import calculate_diversity_metrics

import tabs.tab1_composicion as tab1
import tabs.tab2_dominancia as tab2
import tabs.tab3_comparativos as tab3
import tabs.tab4_espacial as tab4
import tabs.tab5_multivariados as tab5
import tabs.tab6_rareza as tab6
import tabs.tab7_ratios as tab7
import tabs.tab8_16s_vs_18s as tab8
import tabs.tab9_glmm as tab9

# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Dashboard Microbiomas",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
    .sub-header  { font-size: 1.5rem; color: #2ca02c; margin-top: 2rem; }
    .info-box    { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

st.markdown('<p class="main-header">🦠 Análisis de Microbiomas</p>', unsafe_allow_html=True)
st.markdown("### Análisis integrado de comunidades microbianas 16S (Procariotas) y 18S (Eucariotas)")

# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.header("📂 Carga de Datos")

st.sidebar.subheader("1️⃣ Metadata y Variables Ambientales")
metadata_16s_file = st.sidebar.file_uploader("Metadata 16S (.tsv)", type=['tsv', 'txt'])
metadata_18s_file = st.sidebar.file_uploader("Metadata 18S (.tsv)", type=['tsv', 'txt'])

st.sidebar.subheader("2️⃣ Archivos de OTUs")
upload_mode = st.sidebar.radio(
    "Tipo de archivo:",
    ["Feature table + Taxonomy", "Archivos por phylum (legacy)"]
)

otu_files = None
feature_table_16s = taxonomy_16s = feature_table_18s = taxonomy_18s = None

if upload_mode == "Feature table + Taxonomy":
    st.sidebar.markdown("**📊 Datos 16S (Procariotas)**")
    feature_table_16s = st.sidebar.file_uploader("Feature table 16S (.tsv)", type=['tsv', 'txt'], key='ft16s')
    taxonomy_16s     = st.sidebar.file_uploader("Taxonomy 16S (.tsv)",      type=['tsv', 'txt'], key='tax16s')

    st.sidebar.markdown("**📊 Datos 18S (Eucariotas)**")
    feature_table_18s = st.sidebar.file_uploader("Feature table 18S (.tsv)", type=['tsv', 'txt'], key='ft18s')
    taxonomy_18s      = st.sidebar.file_uploader("Taxonomy 18S (.tsv)",      type=['tsv', 'txt'], key='tax18s')

    st.sidebar.info("Puedes subir solo 16S, solo 18S, o ambos")
else:
    st.sidebar.info("Sube TODOS los archivos .tsv de phylums (16S y 18S)")
    otu_files = st.sidebar.file_uploader(
        "Archivos de OTUs (.tsv)", type=['tsv', 'txt'], accept_multiple_files=True
    )

# =============================================================================
# PROCESAMIENTO DE DATOS
# =============================================================================

files_uploaded = False
otu_data = {}

if upload_mode == "Feature table + Taxonomy":
    if feature_table_16s and taxonomy_16s:
        files_uploaded = True
        st.header("📊 Procesamiento de Datos")
        with st.spinner("Procesando 16S..."):
            otu_data.update(load_feature_table_with_taxonomy(feature_table_16s, taxonomy_16s))

    if feature_table_18s and taxonomy_18s:
        files_uploaded = True
        if not otu_data:
            st.header("📊 Procesamiento de Datos")
        with st.spinner("Procesando 18S..."):
            otu_data.update(load_feature_table_with_taxonomy(feature_table_18s, taxonomy_18s))

elif upload_mode == "Archivos por phylum (legacy)" and otu_files:
    files_uploaded = True
    st.header("📊 Procesamiento de Datos")
    with st.spinner("Procesando archivos de OTUs..."):
        otu_data = load_and_process_otus(otu_files)

# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================

if files_uploaded and otu_data:
    # Cargar metadata
    metadata_16s = metadata_18s = None

    if metadata_16s_file:
        metadata_16s = load_metadata(metadata_16s_file)
        if metadata_16s is not None:
            st.success(f"✅ Metadata 16S: {len(metadata_16s)} muestras")

    if metadata_18s_file:
        metadata_18s = load_metadata(metadata_18s_file)
        if metadata_18s is not None:
            st.success(f"✅ Metadata 18S: {len(metadata_18s)} muestras")

    # Construir matrices de composición y diversidad
    composition_data = {}
    diversity_data   = {}
    merged_data      = {}

    for dataset_name, df_otus in otu_data.items():
        df_composition = create_composition_matrix(df_otus, level='Phylum')
        composition_data[dataset_name] = df_composition
        diversity_data[dataset_name]   = calculate_diversity_metrics(df_composition)

        if dataset_name == '16S' and metadata_16s is not None:
            merged_data['16S'] = merge_with_metadata(df_composition, metadata_16s)
        elif dataset_name == '18S' and metadata_18s is not None:
            merged_data['18S'] = merge_with_metadata(df_composition, metadata_18s)

    # Renderizar tabs
    st_tab1, st_tab2, st_tab3, st_tab4, st_tab5, st_tab6, st_tab7, st_tab8, st_tab9 = st.tabs([
        "📊 Composición", "👑 Dominancia", "⚖️ Comparativos",
        "🗺️ Espacial",    "🔢 Multivariados", "💎 Rareza",
        "📐 Ratios",      "🔬 16S vs 18S",   "📈 GLMM"
    ])

    with st_tab1: tab1.render(composition_data)
    with st_tab2: tab2.render(composition_data, diversity_data)
    with st_tab3: tab3.render(diversity_data)
    with st_tab4: tab4.render(composition_data, diversity_data, {'16S': metadata_16s, '18S': metadata_18s})
    with st_tab5: tab5.render(composition_data)
    with st_tab6: tab6.render(composition_data)
    with st_tab7: tab7.render(composition_data)
    with st_tab8: tab8.render(composition_data, diversity_data)
    with st_tab9: tab9.render(diversity_data, merged_data, metadata_16s, metadata_18s)

else:
    st.info("""
    ### 👋 Bienvenido al Dashboard de Análisis de Microbiomas

    Para comenzar:
    1. **Carga los archivos de metadata** (16S y/o 18S) en la barra lateral
    2. **Sube los archivos de OTUs** (.tsv)
    3. El dashboard procesará automáticamente los datos

    #### 📁 Estructura esperada de archivos:

    **Metadata (.tsv):** SampleID, Site, Class (SED/PLA), variables ambientales
    - 16S: sin prefijo (ej: 1PLA, 8SED)
    - 18S: con prefijo E_ (ej: E_1PLA, E_8SED)

    **Archivos de OTUs (.tsv):**
    - Primera columna: #OTU ID (con taxonomía completa)
    - Resto: muestras con abundancias
    """)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>Dashboard de Análisis de Microbiomas v1.0</p>
    <p>Desarrollado con Streamlit 🎈 | 2026</p>
</div>
""", unsafe_allow_html=True)
