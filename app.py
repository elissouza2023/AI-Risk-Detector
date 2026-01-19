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
        return  # não quebra o app se a imagem não existir

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

        /* CONTAINER PRINCIPAL */
        .block-container {{
            background-color: rgba(0, 0, 0, 0.70);
            padding: 2rem;
            border-radius: 12px;
        }}

        html, body, [class*="css"] {{
            color: #EAF2F8;
        }}

        h1, h2, h3 {{
            color: #00E5FF;
        }}

        textarea, input {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            color: #EAF2F8 !important;
        }}

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
# TÍTULO E DESCRIÇÃO
# ======================================================
st.title("🔐 Detector de Risco no Uso de IA")
st.write(
    "Esta ferramenta analisa prompts e identifica riscos relacionados "
    "ao uso de Inteligência Artificial em ambientes corporativos, "
    "combinando regras de segurança (Regex) e NLP."
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
# REGEX – DETECÇÃO DIRETA
# ======================================================
def detectar_risco_regex(texto):
    texto = texto.lower()

    # CPF
    if re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', texto):
        return "dado_pessoal"

    # Email
    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', texto):
        return "dado_pessoal"

    # Credenciais
    if re.search(r'\b(senha|password|token|api key|credencial)\b', texto):
        return "credencial"

    return "baixo_risco"

# ======================================================
# CLASSIFICAÇÃO FINAL (REGEX + NLP)
# ======================================================
def classificar_risco(texto):
    risco_regex = detectar_risco_regex(texto)

    if risco_regex != "baixo_risco":
        return risco_regex, "regex"

    texto_vec = vectorizer.transform([texto])
    risco_nlp = model.predict(texto_vec)[0]

    return risco_nlp, "nlp"

# ======================================================
# ANÁLISE DE PROMPT ÚNICO
# ======================================================
st.subheader("✍️ Análise de Prompt Único")

texto_usuario = st.text_area(
    "Digite um prompt para análise de risco:",
    height=150
)

if st.button("🔍 Analisar Prompt"):
    if texto_usuario.strip() == "":
        st.warning("Digite um texto para análise.")
    else:
        risco, metodo = classificar_risco(texto_usuario)

        if risco == "baixo_risco":
            st.success(f"✅ Risco detectado: {risco} (via {metodo})")
        elif risco == "credencial":
            st.warning(f"⚠️ Risco detectado: {risco} (via {metodo})")
        else:
            st.error(f"🚨 Risco detectado: {risco} (via {metodo})")

# ======================================================
# ANÁLISE EM LOTE (CSV)
# ======================================================
st.subheader("📂 Análise em Lote (CSV)")

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
