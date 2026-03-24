"""
Tab 9: Modelos Lineales Generalizados Mixtos (GLMM)
"""

import traceback

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import statsmodels.api as sm
from scipy import stats
from statsmodels.regression.mixed_linear_model import MixedLM


ENV_VARS = [
    'pH', 'Temp_C', 'Conductivity-mS/cm', 'DisO2-mg/L', '%SAT',
    'Cl-mg/L', 'BOD-mg/L', 'QOD-mg/L', 'Seston-g/L',
    'PO4-mg/L', 'NH4+mg/L', 'NO3-x-g/L', 'Clorofila-a ug/L'
]

RESPONSE_OPTIONS = {
    'Shannon': 'Shannon',
    'Riqueza de Phylums': 'Richness',
    'Índice de Simpson': 'Simpson',
    'Equitatividad de Pielou': 'Pielou'
}

SAMPLE_ID_NAMES = ['SampleID', 'Sample', '#SampleID', 'sample_id', 'Sample_ID']


def _find_sample_col(df):
    return next((n for n in SAMPLE_ID_NAMES if n in df.columns), None)


def _run_model(df_model, response_var, x_vars, include_site):
    y = df_model[response_var].values
    X = df_model[x_vars].astype(float)
    X = sm.add_constant(X)

    if include_site and 'Site' in df_model.columns:
        groups = df_model['Site'].values
        model = MixedLM(y, X, groups=groups)
        return model.fit(method='powell')
    else:
        model = sm.OLS(y, X)
        return model.fit()


def _show_results(result, df_model, selected_predictors, response_var, response_choice, dataset_choice):
    st.success("✅ Modelo ajustado exitosamente!")
    st.markdown("### 📋 Resumen del Modelo")

    coef_df = pd.DataFrame({
        'Variable': result.params.index,
        'Coeficiente (β)': result.params.values,
        'Error Estándar': result.bse.values,
        'p-value': result.pvalues.values,
        'Significancia': [
            '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
            for p in result.pvalues.values
        ]
    })
    st.dataframe(coef_df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if hasattr(result, 'aic'):
            st.metric("AIC", f"{result.aic:.2f}")
    with col2:
        if hasattr(result, 'bic'):
            st.metric("BIC", f"{result.bic:.2f}")
    with col3:
        if hasattr(result, 'rsquared'):
            st.metric("R²", f"{result.rsquared:.3f}")

    st.markdown("#### Visualización de Efectos")
    import plotly.express as px
    for pred in selected_predictors:
        fig = px.scatter(
            df_model, x=pred, y=response_var,
            color='Type' if 'Type' in df_model.columns else None,
            trendline='ols',
            title=f'Efecto de {pred} sobre {response_choice}',
            labels={pred: pred, response_var: response_choice},
            color_discrete_map={'SED': 'chocolate', 'PLA': 'steelblue'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Diagnósticos del Modelo")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].scatter(result.fittedvalues, result.resid, alpha=0.6)
    axes[0].axhline(y=0, color='r', linestyle='--')
    axes[0].set_xlabel('Valores predichos')
    axes[0].set_ylabel('Residuos')
    axes[0].set_title('Residuos vs Valores Predichos')
    axes[0].grid(alpha=0.3)

    stats.probplot(result.resid, dist="norm", plot=axes[1])
    axes[1].set_title('Q-Q Plot')
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    with st.expander("📄 Ver resumen completo del modelo"):
        st.text(str(result.summary()))

    st.markdown("### 💾 Exportar Resultados")
    csv_coef = coef_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar tabla de coeficientes (CSV)",
        data=csv_coef,
        file_name=f'glmm_coefficients_{dataset_choice}_{response_choice}.csv',
        mime='text/csv',
    )


def render(diversity_data, merged_data, metadata_16s, metadata_18s):
    st.header("📈 Modelos Lineales Generalizados Mixtos (GLMM)")

    if not merged_data:
        st.warning("⚠️ Necesitas cargar los archivos de metadata para usar GLMM")
        return

    dataset_choice = st.selectbox(
        "Selecciona dataset:", list(merged_data.keys()), key='glmm_dataset'
    )
    df_diversity = diversity_data[dataset_choice]
    df_metadata_full = metadata_16s if dataset_choice == '16S' else metadata_18s

    if df_metadata_full is None:
        st.error(f"❌ No hay metadata cargada para {dataset_choice}")
        return

    sample_col = _find_sample_col(df_metadata_full)
    if sample_col is None:
        st.error(f"❌ No se encontró columna de SampleID. Columnas: {df_metadata_full.columns.tolist()}")
        return

    df_div_copy = df_diversity.copy()
    df_div_copy['SampleID'] = df_div_copy['Sample']

    df_meta_copy = df_metadata_full.copy()
    if sample_col != 'SampleID':
        df_meta_copy = df_meta_copy.rename(columns={sample_col: 'SampleID'})

    df_merged = df_div_copy.merge(df_meta_copy, on='SampleID', how='left')

    st.subheader("Configuración del Modelo")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 1️⃣ Variable Respuesta")
        response_choice = st.selectbox("Variable dependiente:", list(RESPONSE_OPTIONS.keys()))
        response_var = RESPONSE_OPTIONS[response_choice]

    with col2:
        st.markdown("### 2️⃣ Estructura del Modelo")
        include_type = st.checkbox("Incluir Tipo de muestra (SED vs PLA)", value=True)
        include_site = st.checkbox("Incluir Sitio como efecto aleatorio", value=True)

    st.markdown("### 3️⃣ Predictores Ambientales")
    available_env_vars = [v for v in ENV_VARS if v in df_merged.columns]

    if not available_env_vars:
        st.error("❌ No se encontraron variables ambientales en la metadata")
        st.info(f"Columnas disponibles: {df_merged.columns.tolist()}")
        return

    selected_predictors = st.multiselect(
        "Selecciona predictores (puedes elegir múltiples):",
        available_env_vars,
        default=[]
    )

    if not selected_predictors:
        st.info("👆 Selecciona al menos un predictor ambiental para ejecutar el modelo")
        return

    st.markdown("### 4️⃣ Ejecutar Modelo")
    if not st.button("▶ EJECUTAR GLMM", type="primary"):
        return

    with st.spinner("Ajustando modelo..."):
        try:
            df_model = df_merged.copy()

            if response_var not in df_model.columns:
                st.error(f"❌ Variable {response_var} no encontrada. Columnas: {df_model.columns.tolist()}")
                return

            df_model[response_var] = pd.to_numeric(df_model[response_var], errors='coerce')
            for var in selected_predictors:
                df_model[var] = pd.to_numeric(df_model[var], errors='coerce')

            vars_to_check = [response_var] + selected_predictors

            if include_type and 'Type' in df_model.columns:
                df_model['Type_dummy'] = (df_model['Type'] == 'PLA').astype(int)
                vars_to_check.append('Type_dummy')

            if include_site and 'Site' in df_model.columns:
                vars_to_check.append('Site')

            st.info(f"📊 Datos antes de eliminar NaN: {len(df_model)} filas")

            nan_counts = df_model[vars_to_check].isna().sum()
            if nan_counts.any():
                st.write("**NaN por variable:**")
                st.dataframe(nan_counts[nan_counts > 0])

            df_model = df_model.dropna(subset=vars_to_check)
            st.info(f"📊 Datos después de eliminar NaN: {len(df_model)} filas")

            if len(df_model) < 5:
                st.error(f"""
                ❌ Solo {len(df_model)} filas válidas (mínimo 5).
                Sugerencias:
                1. Revisa tu metadata - puede haber muchos valores faltantes
                2. Selecciona menos predictores
                3. Usa variables con pocos NaN
                """)
                return

            x_vars = selected_predictors.copy()
            if include_type and 'Type_dummy' in df_model.columns:
                x_vars.append('Type_dummy')

            result = _run_model(df_model, response_var, x_vars, include_site)
            _show_results(result, df_model, selected_predictors, response_var, response_choice, dataset_choice)

        except Exception as e:
            st.error(f"❌ Error al ajustar el modelo: {e}")
            st.code(traceback.format_exc())
