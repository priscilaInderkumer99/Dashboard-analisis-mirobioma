"""
Tab 5: Análisis Multivariados (PCA, NMDS, Clustering)
"""

import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.manifold import MDS

from utils.diversity import hellinger_transform


def render(composition_data):
    st.header("🔢 Análisis Multivariados")

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(composition_data.keys()), key='multi_dataset'
    )
    df_comp = composition_data[dataset_choice]

    subtab1, subtab2, subtab3 = st.tabs(["PCA", "NMDS", "Clustering"])

    with subtab1:
        st.subheader("Análisis de Componentes Principales (PCA)")

        n_samples, n_features = len(df_comp), len(df_comp.columns)

        if n_samples < 2 or n_features < 2:
            st.warning(f"⚠️ PCA requiere al menos 2 muestras y 2 phylums. Tienes {n_samples} y {n_features}.")
        else:
            df_hellinger = hellinger_transform(df_comp)
            n_components = min(2, n_samples, n_features)
            pca = PCA(n_components=n_components)
            pca_coords = pca.fit_transform(df_hellinger)

            if n_components == 2:
                import pandas as pd
                df_pca = pd.DataFrame({
                    'PC1': pca_coords[:, 0],
                    'PC2': pca_coords[:, 1],
                    'Sample': df_comp.index,
                    'Type': ['SED' if 'SED' in s else 'PLA' for s in df_comp.index]
                })

                fig = px.scatter(
                    df_pca, x='PC1', y='PC2', color='Type',
                    color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                    symbol='Type', text='Sample',
                    title=(
                        f'PCA - {dataset_choice}<br>'
                        f'Varianza explicada: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, '
                        f'PC2={pca.explained_variance_ratio_[1]*100:.1f}%'
                    ),
                    labels={
                        'PC1': f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)',
                        'PC2': f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)'
                    }
                )
                fig.update_traces(textposition='top center', textfont_size=8)
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Solo se pudo calcular 1 componente. Se necesitan al menos 2 para visualización 2D.")

    with subtab2:
        st.subheader("Non-metric Multidimensional Scaling (NMDS)")

        if df_comp.shape[1] >= 2:
            df_hellinger = hellinger_transform(df_comp)
            distances = pdist(df_hellinger.values, metric='braycurtis')
            dist_matrix = squareform(distances)

            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, n_init=10)
            nmds_coords = mds.fit_transform(dist_matrix)

            import pandas as pd
            df_nmds = pd.DataFrame({
                'NMDS1': nmds_coords[:, 0],
                'NMDS2': nmds_coords[:, 1],
                'Sample': df_comp.index,
                'Type': ['SED' if 'SED' in s else 'PLA' for s in df_comp.index]
            })

            fig = px.scatter(
                df_nmds, x='NMDS1', y='NMDS2', color='Type',
                color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'},
                symbol='Type', text='Sample',
                title=f'NMDS (Bray-Curtis) - {dataset_choice}<br>Stress: {mds.stress_:.3f}'
            )
            fig.update_traces(textposition='top center', textfont_size=8)
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            if mds.stress_ > 0.2:
                st.warning(f"⚠️ Stress = {mds.stress_:.3f}. Valores >0.2 indican ajuste pobre.")
        else:
            st.warning("Se necesitan al menos 2 phylums para NMDS")

    with subtab3:
        st.subheader("Clustering Jerárquico")

        df_hellinger = hellinger_transform(df_comp)
        linkage_matrix = linkage(df_hellinger.values, method='ward')

        fig, ax = plt.subplots(figsize=(12, 6))
        dendrogram(
            linkage_matrix,
            labels=df_comp.index.tolist(),
            ax=ax,
            leaf_font_size=8,
            orientation='top'
        )
        ax.set_title(f'Dendrograma (Ward linkage) - {dataset_choice}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Muestra', fontsize=12)
        ax.set_ylabel('Distancia', fontsize=12)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)
