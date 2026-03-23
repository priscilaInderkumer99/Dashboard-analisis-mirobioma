"""
Funciones de carga y procesamiento de datos (OTUs, taxonomy, metadata)
"""

import io
import streamlit as st
import pandas as pd

from utils.diversity import (
    detect_dataset_type,
    extract_phylum,
    extract_genus,
)


@st.cache_data
def load_and_process_otus(uploaded_files):
    """
    Carga y procesa archivos de OTUs (formato legacy por phylum).
    Retorna diccionario con datos 16S y 18S separados.
    """
    data_16s = []
    data_18s = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            file_content = uploaded_file.read().decode('utf-8')
            lines = file_content.split('\n')

            header_line = [line for line in lines if line.startswith('#OTU ID')][0]
            sample_names = header_line.strip().split('\t')

            df = pd.read_csv(io.StringIO(file_content), sep="\t", header=None, comment='#')
            df.columns = sample_names
            df.rename(columns={'#OTU ID': 'OTU_ID'}, inplace=True)

            sample_cols = [col for col in df.columns if col != 'OTU_ID']
            df[sample_cols] = df[sample_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

            dataset_type = detect_dataset_type(sample_cols)
            df['Phylum'] = df['OTU_ID'].apply(extract_phylum)
            df['Genus'] = df['OTU_ID'].apply(extract_genus)

            if dataset_type == '16S':
                data_16s.append(df)
            else:
                data_18s.append(df)

            status_text.text(f"✓ {uploaded_file.name}: {dataset_type} - {len(df)} OTUs")

        except Exception as e:
            st.error(f"Error procesando {uploaded_file.name}: {e}")

        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.empty()
    progress_bar.empty()

    result = {}

    if data_16s:
        df_16s = pd.concat(data_16s, ignore_index=True)
        result['16S'] = df_16s
        st.success(f"✅ 16S: {len(df_16s)} OTUs totales")

    if data_18s:
        df_18s = pd.concat(data_18s, ignore_index=True)
        result['18S'] = df_18s
        st.success(f"✅ 18S: {len(df_18s)} OTUs totales")

    return result


@st.cache_data
def load_feature_table_with_taxonomy(feature_table_file, taxonomy_file):
    """
    Carga feature table y taxonomy, los relaciona y retorna formato compatible.
    """
    try:
        ft_content = feature_table_file.read().decode('utf-8')
        ft_lines = ft_content.split('\n')

        lines_filtered = [line for line in ft_lines
                          if not line.startswith('#') or line.startswith('#OTU ID')]
        ft_clean = '\n'.join(lines_filtered)
        df_ft = pd.read_csv(io.StringIO(ft_clean), sep="\t")
        df_ft.rename(columns={'#OTU ID': 'Feature ID'}, inplace=True)

        tax_content = taxonomy_file.read().decode('utf-8')
        df_tax = pd.read_csv(io.StringIO(tax_content), sep="\t")

        # DEBUG - ver columnas reales
        st.write("Columnas taxonomy:", df_tax.columns.tolist())
        st.write("Columnas feature table:", df_ft.columns.tolist())

        # Renombrar por posición (robusto ante variaciones de nombre)
        df_tax.columns = ['Feature ID', 'Taxon'] + df_tax.columns[2:].tolist()

        df_merged = df_ft.merge(df_tax[['Feature ID', 'Taxon']], on='Feature ID', how='left')
        df_merged.rename(columns={'Feature ID': 'OTU_ID', 'Taxon': 'Taxonomy'}, inplace=True)

        df_merged['Phylum'] = df_merged['Taxonomy'].apply(extract_phylum)
        df_merged['Genus'] = df_merged['Taxonomy'].apply(extract_genus)

        sample_cols = [col for col in df_merged.columns if col not in ['OTU_ID', 'Taxonomy', 'Phylum', 'Genus']]
        df_merged[sample_cols] = df_merged[sample_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        dataset_type = detect_dataset_type(sample_cols)
        n_phylums = df_merged['Phylum'].nunique()

        st.success(f"✅ {dataset_type}: {len(df_merged)} OTUs, {len(sample_cols)} muestras, {n_phylums} phylums")

        return {dataset_type: df_merged}

    except Exception as e:
        st.error(f"❌ Error procesando archivos: {e}")
        import traceback
        st.code(traceback.format_exc())
        return {}

@st.cache_data
def load_metadata(uploaded_file):
    """Carga archivo de metadata (.tsv)"""
    try:
        df = pd.read_csv(uploaded_file, sep='\t')
        
        # Convertir decimales con coma a punto
        for col in df.columns:
            try:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df
    except Exception as e:
        st.error(f"Error cargando metadata: {e}")
        return None

def create_composition_matrix(df_otus, level='Phylum'):
    """
    Crea matriz de composición a nivel de phylum o genus.
    Filas = muestras, Columnas = taxones.
    """
    sample_cols = [col for col in df_otus.columns if col not in ['OTU_ID', 'Phylum', 'Genus', 'Taxonomy']]
    df_otus[sample_cols] = df_otus[sample_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    df_grouped = df_otus.groupby(level)[sample_cols].sum()
    return df_grouped.T


def merge_with_metadata(df_composition, df_metadata):
    """Une datos de composición con metadata"""
    df_comp = df_composition.copy()
    df_comp['SampleID'] = df_comp.index

    possible_names = ['SampleID', 'Sample', '#SampleID', 'sample_id', 'sample-id', 'Sample_ID']
    sample_col = next((n for n in possible_names if n in df_metadata.columns), None)

    if sample_col is None:
        st.error(f"❌ No se encontró columna de SampleID en metadata. Columnas: {df_metadata.columns.tolist()}")
        return df_comp

    if sample_col != 'SampleID':
        df_metadata = df_metadata.rename(columns={sample_col: 'SampleID'})

    return df_comp.merge(df_metadata, on='SampleID', how='left')
