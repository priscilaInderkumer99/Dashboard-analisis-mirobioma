# Manual de Usuario — Dashboard de Análisis de Microbiomas

## ¿Qué es este dashboard?

Este dashboard es una herramienta interactiva para analizar comunidades microbianas de muestras de sedimento y plancton de un río. Permite explorar quiénes están presentes (composición), cuántos hay (diversidad), dónde están (espacial) y qué factores ambientales los afectan (GLMM), sin necesidad de escribir código.

---

## Cómo instalar y correr el dashboard

### Requisitos previos
- Python 3.8 o superior instalado en tu computadora
- Conexión a internet para la instalación inicial

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/priscilaInderkumer99/dashboard-microbiomas.git
cd dashboard-microbiomas

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Linux/Mac
venv\Scripts\activate           # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Correr el dashboard
streamlit run app.py
```

El dashboard se abre automáticamente en el navegador. Si no se abre, copiá la dirección que aparece en la terminal (ej: `http://localhost:8501`) y pegala en el navegador.

---

## Cómo cargar los datos

En la barra lateral izquierda vas a encontrar el panel de carga. Seguí este orden:

**Paso 1 — Metadata**
- Subí el archivo de metadata 16S (.tsv)
- Subí el archivo de metadata 18S (.tsv)

**Paso 2 — Archivos de OTUs**
- Seleccioná el modo "Feature table + Taxonomy"
- Subí la feature table 16S y su taxonomy correspondiente
- Subí la feature table 18S y su taxonomy correspondiente
- Podés cargar solo 16S, solo 18S, o ambos

Una vez cargados los archivos, el dashboard procesa los datos automáticamente y habilita todos los análisis. Vas a ver mensajes verdes confirmando cuántos OTUs y phylums se detectaron.

---

## Guía de cada sección

### 📊 Composición
Muestra qué grupos de microorganismos (phylums) están presentes en cada muestra y en qué proporción.

- **Barras apiladas**: cada barra es una muestra, cada color es un phylum. La altura de cada color indica qué porcentaje representa ese phylum en esa muestra.
- **Heatmap**: vista alternativa en grilla. Los colores más intensos indican mayor abundancia.
- **Tabla**: los números crudos para descargar.

Podés filtrar para ver solo muestras de sedimento (SED) o plancton (PLA).

---

### 👑 Dominancia
Analiza si las comunidades están dominadas por pocos grupos o son más equitativas.

- **Índice de Simpson**: mide dominancia. Valores cercanos a 1 indican que pocos phylums dominan la comunidad.
- **Equitatividad de Pielou**: mide qué tan equitativamente distribuidas están las abundancias. Valores cercanos a 1 indican distribución más uniforme.
- **Riqueza**: cantidad de phylums distintos detectados en cada muestra.
- **Curvas rango-abundancia**: muestra los phylums ordenados de más a menos abundante. Curvas más pronunciadas indican mayor dominancia.
- **Core vs Raros**: clasifica los phylums según en qué porcentaje de muestras aparecen.

---

### ⚖️ Comparativos
Compara la diversidad entre muestras de sedimento y plancton usando estadística.

Los gráficos de caja (boxplots) muestran la distribución de cada métrica para SED y PLA. La tabla de tests estadísticos (Mann-Whitney U) indica si las diferencias son significativas:

- `ns` = no significativo (p > 0.05): no hay diferencia real entre SED y PLA
- `*` = p < 0.05: diferencia moderada
- `**` = p < 0.01: diferencia importante
- `***` = p < 0.001: diferencia muy marcada

---

### 🗺️ Espacial
Analiza cómo cambia la comunidad a lo largo del río.

- **Gradientes longitudinales**: muestra cómo varía la diversidad (Shannon, Simpson, etc.) de un sitio al otro. La línea de tendencia (LOWESS) ayuda a ver si hay un patrón gradual.
- **Composición por sitio**: elegís un sitio y ves la composición de SED vs PLA lado a lado.
- **Mapa de sitios**: mapa interactivo con los puntos de muestreo sobre el río. Podés colorear los puntos por diversidad y seleccionar un sitio para ver su composición.

---

### 🔢 Multivariados
Analiza similitudes y diferencias entre muestras usando todas las variables a la vez.

- **PCA**: reduce la información de todos los phylums a dos ejes. Muestras cercanas en el gráfico tienen comunidades similares. Los porcentajes en los ejes indican cuánta variación explica cada componente.
- **NMDS**: similar al PCA pero basado en distancias de Bray-Curtis, más adecuado para datos de abundancia. El valor de "stress" indica la calidad del gráfico — valores menores a 0.2 son aceptables.
- **Clustering jerárquico**: dendrograma que agrupa las muestras más similares entre sí.

---

### 💎 Rareza
Identifica phylums exclusivos de cada ambiente y los que aparecen raramente.

- **Taxa únicos**: phylums que solo aparecen en sedimento, solo en plancton, o en ambos.
- **Proporción de raros**: podés ajustar el umbral de "rareza" y ver qué porcentaje de phylums son raros en cada muestra.

---

### 📐 Ratios
Calcula cocientes entre dos phylums y correlaciones.

Útil para analizar relaciones ecológicas conocidas, por ejemplo el ratio entre dos grupos competidores. El test de Spearman indica si la correlación entre dos phylums es estadísticamente significativa.

---

### 🔬 16S vs 18S
Compara la diversidad de procariotas (bacterias/arqueas, 16S) con eucariotas (algas, hongos, protozoos, 18S).

Solo disponible si cargaste datos de ambos tipos.

---

### 📈 GLMM — Modelos Lineales Mixtos

Esta sección responde la pregunta: **¿qué variables ambientales explican la diversidad microbiana?**

#### Cómo usarlo paso a paso

**Paso 1 — Elegí la variable respuesta**
Es lo que querés explicar. Por ejemplo, seleccioná "Shannon" si querés saber qué afecta la diversidad general de la comunidad.

**Paso 2 — Estructura del modelo**
- "Incluir tipo de muestra (SED vs PLA)": activalo si creés que el tipo de muestra afecta la diversidad (recomendado).
- "Incluir sitio como efecto aleatorio": activalo si querés controlar que muestras del mismo sitio no son independientes (recomendado).

**Paso 3 — Elegí los predictores ambientales**
Son las variables que podrían estar causando cambios en la diversidad. Recomendaciones:
- Empezá con 1 o 2 variables (ej: pH, oxígeno disuelto)
- No uses más de 1 predictor cada 5 muestras
- Evitá combinar variables muy relacionadas entre sí (ej: temperatura y oxígeno disuelto suelen correlacionarse)

**Paso 4 — Ejecutá el modelo**
Hacé clic en "▶ EJECUTAR GLMM".

#### Cómo interpretar los resultados

**Tabla de coeficientes**

| Columna | Qué significa |
|---------|---------------|
| Coeficiente (β) | Dirección y magnitud del efecto. Positivo = mayor valor de la variable → mayor diversidad. Negativo = lo contrario. |
| Error estándar | Cuánta incertidumbre hay en la estimación. |
| p-value | Probabilidad de que el efecto sea producto del azar. |
| Significancia | `*` p<0.05, `**` p<0.01, `***` p<0.001, `ns` no significativo |

**Ejemplo de interpretación**: si el coeficiente de pH es 0.45 con p=0.02 (`*`), significa que a mayor pH, mayor diversidad Shannon, y esa relación es estadísticamente significativa.

**AIC**: criterio para comparar modelos. Menor AIC = mejor modelo. Si agregás un predictor y el AIC baja más de 2 puntos, ese predictor mejora el modelo.

**R²**: proporción de la variación en diversidad que explica el modelo. Un R²=0.60 significa que el modelo explica el 60% de la variación observada.

**Gráficos de diagnóstico**
- "Residuos vs Valores Predichos": los puntos deberían estar distribuidos aleatoriamente alrededor de la línea roja. Patrones sistemáticos indican que el modelo no es adecuado.
- "Q-Q Plot": los puntos deberían seguir la línea diagonal. Desviaciones grandes indican que los residuos no son normales.

---

## Preguntas frecuentes

**¿Por qué el mapa no muestra los puntos?**
Verificá que la metadata tenga columnas `Lat` y `Long` con coordenadas en formato grados/minutos/segundos (ej: `34°45'05.2"S`).

**¿Por qué el GLMM dice "pocas filas válidas"?**
Probablemente hay muchos valores faltantes en la metadata para las variables que seleccionaste. Probá con menos predictores o verificá que la metadata tenga datos completos.

**¿Por qué solo aparece un phylum en los gráficos?**
Verificá que el archivo de taxonomy use el formato correcto con prefijos `p__`, `g__`, etc. y separador `; ` (punto y coma seguido de espacio).

**¿Puedo usar solo 16S o solo 18S?**
Sí. El tab de comparación 16S vs 18S solo se activa cuando tenés ambos, pero el resto de los análisis funcionan con cualquiera de los dos.

---

## Autora

**Priscila Inderkumer**
2026
