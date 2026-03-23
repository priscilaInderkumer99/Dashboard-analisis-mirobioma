"""
Funciones de cálculo de diversidad y métricas ecológicas
"""

import numpy as np
import pandas as pd
from scipy.stats import entropy


def detect_dataset_type(sample_columns):
    """Detecta si las muestras son 16S o 18S basado en prefijo E_"""
    has_E_prefix = any(col.startswith('E_') for col in sample_columns)
    return '18S' if has_E_prefix else '16S'


def extract_phylum(taxonomy):
    if pd.isna(taxonomy):
        return "Unknown"
    parts = str(taxonomy).split(';')
    for part in parts:
        part = part.strip()  # <-- esto elimina espacios adelante
        if part.startswith('p__'):
            phylum = part.replace('p__', '').strip()
            return phylum if phylum else "Unassigned"
    return "Unassigned"

def extract_genus(taxonomy):
    if pd.isna(taxonomy):
        return "Unknown"
    parts = str(taxonomy).split(';')
    for part in parts:
        part = part.strip()  # <-- ídem
        if part.startswith('g__'):
            genus = part.replace('g__', '').strip()
            return genus if genus else "Unassigned"
    return "Unassigned"

def shannon_diversity(abundances):
    """Calcula índice de Shannon"""
    abundances = pd.to_numeric(abundances, errors='coerce').fillna(0)
    abundances = abundances[abundances > 0]
    if len(abundances) == 0:
        return 0
    proportions = abundances / abundances.sum()
    return entropy(proportions, base=np.e)


def simpson_index(abundances):
    """Calcula índice de Simpson"""
    abundances = pd.to_numeric(abundances, errors='coerce').fillna(0)
    if abundances.sum() == 0:
        return 0
    proportions = abundances / abundances.sum()
    return 1 - np.sum(proportions ** 2)


def pielou_evenness(abundances):
    """Calcula equitatividad de Pielou"""
    abundances = pd.to_numeric(abundances, errors='coerce').fillna(0)
    shannon = shannon_diversity(abundances)
    richness = (abundances > 0).sum()
    if richness <= 1:
        return 0
    return shannon / np.log(richness)


def calculate_diversity_metrics(df_composition):
    """Calcula todas las métricas de diversidad para un DataFrame"""
    metrics = pd.DataFrame({
        'Sample': df_composition.index,
        'Shannon': df_composition.apply(shannon_diversity, axis=1),
        'Simpson': df_composition.apply(simpson_index, axis=1),
        'Pielou': df_composition.apply(pielou_evenness, axis=1),
        'Richness': (df_composition > 0).sum(axis=1),
        'Total_reads': df_composition.sum(axis=1)
    })
    metrics['Type'] = ['SED' if 'SED' in s else 'PLA' for s in metrics['Sample']]
    metrics['Site'] = metrics['Sample'].str.extract(r'(?:E_)?([^_]+?)(?:SED|PLA)')[0]
    return metrics

def dms_to_decimal(coord_str):
    """Convierte coordenadas DMS (34°45'05.2"S) a decimal (-34.751)"""
    import re
    if pd.isna(coord_str) or str(coord_str).strip() == '':
        return None
    coord_str = str(coord_str).strip()
    # Extraer componentes
    match = re.match(r"(\d+)°\s*(\d+)'?\s*([\d.]+)?\"?\s*([NSEW])", coord_str)
    if not match:
        return None
    degrees = float(match.group(1))
    minutes = float(match.group(2))
    seconds = float(match.group(3)) if match.group(3) else 0.0
    direction = match.group(4)
    decimal = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def hellinger_transform(df):
    """Transformación Hellinger"""
    df_relative = df.div(df.sum(axis=1), axis=0).fillna(0)
    return np.sqrt(df_relative)
