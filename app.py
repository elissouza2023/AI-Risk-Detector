import streamlit as st
import pandas as pd
import joblib
import re
import base64
from pathlib import Path

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Detector de Risco no Uso de IA",
    layout="centered"
)

# ======================================================
# FUNÇÃO: FUNDO + CSS
# ======================================================
def set_background(image_file):
    img_path = Path(image_file)
    if not img_path.exists():
        return  # não quebra o app se não achar a imagem

    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Texto geral */
        html, body, [class*="css"] {{
            color: #EAF2F8;
        }}

        /* Títulos */
        h1, h2, h3 {{
            color: #00E5FF;
        }}

        /* Inputs */
        textarea, input {{
            background-color: rgba(0, 0, 0, 0.6) !important;
            color: #EAF2F8 !important;
        }}

        /* Upload */
        .stFileUploader {{
            background-color: rgba(0, 0, 0, 0.6);
            color: #EAF2F8;
        }}

        /* DataFrame */
        [data-testid="stDataFrame"] {{
            background-color: rgba(0, 0, 0, 0.6);
        }}

        /* Botões */
        .stButton>button {{
            background-color: #00E5FF;
            color: #003344;
            border-radius: 8px;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("fundo.jpg")

# ======================================================
# TÍTULO
# ======================================================
st.title("🔐 Detector de Risco no Uso de IA")
st.write(
    "Esta ferramenta analisa prompts e identifica riscos relacionados "
    "ao uso de Inteligência Artificial em ambientes corporativos."
)

# ======================================================
# CARREGAR MODELOS
# ======================================================
@st.cache_resource
def carregar_modelos():
    model = joblib.load("modelo_risco_ia.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

model, vectorizer = carregar_modelos()

# ======================================================
# REGEX
# ======================================================
def detectar_risco_regex(texto):
    texto = texto.lower()

    if re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', texto):
        return "dado_pessoal"

    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', texto):
        return "dado_pessoal"

    if re.search(r'\b(senha|password|token|api key|credencial)\b', texto):
        return "credencial"

    return "baixo_risco"

# ======================================================
# CLASSIFICAÇÃO FINAL
# ======================================================
def classificar_risco(texto):
    risco_regex = detectar_risco_regex(texto)

    if risco_regex != "baixo_risco":
        return risco_regex, "regex"

    texto_vec = vectorizer.transform([texto])
    risco_nlp = model.predict(texto_vec)[0]

    return risco_nlp, "nlp"

# ======================================================
# INTERFACE – CSV
# ======================================================
st.subheader("📂 Análise em lote (CSV)")

arquivo = st.file_uploader(
    "Envie um arquivo CSV com a coluna 'text'",
    type=["csv"]
)

if arquivo is not None:
    df = pd.read_csv(arquivo)

    if "text" not in df.columns:
        st.error("O arquivo CSV deve conter a coluna 'text'.")
    else:
        resultados = []

        for texto in df["text"]:
            risco, metodo = classificar_risco(str(texto))
            resultados.append({
                "text": texto,
                "risco_detectado": risco,
                "metodo": metodo
            })

        df_resultado = pd.DataFrame(resultados)

        st.dataframe(df_resultado)

        # GRÁFICO
        st.subheader("📊 Distribuição dos riscos")
        contagem = df_resultado["risco_detectado"].value_counts()
        st.bar_chart(contagem)

        # DOWNLOAD
        st.download_button(
            "📥 Baixar resultado",
            df_resultado.to_csv(index=False).encode("utf-8"),
            "resultado_analise_risco.csv",
            "text/csv"
        )
