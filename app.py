import streamlit as st
import pandas as pd
import joblib
import re
import base64
from pathlib import Path

def set_background(image_file):
    img_path = Path(image_file)
    if not img_path.exists():
        return  # se não achar a imagem, não quebra o app

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
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(
    page_title="Detector de Risco no Uso de IA",
    layout="centered"
)
set_background("fundo.jpg")

st.title("🔐 Detector de Risco no Uso de IA")
st.write(
    "Esta ferramenta analisa prompts e identifica riscos relacionados "
    "ao uso de IA em ambientes corporativos."
)
@st.cache_resource
def carregar_modelos():
    model = joblib.load("modelo_risco_ia.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

model, vectorizer = carregar_modelos()
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
def classificar_risco(texto):
    # 1️⃣ Regex primeiro
    risco_regex = detectar_risco_regex(texto)

    if risco_regex != "baixo_risco":
        return risco_regex, "regex"

    # 2️⃣ NLP se regex não detectar
    texto_vec = vectorizer.transform([texto])
    risco_nlp = model.predict(texto_vec)[0]

    return risco_nlp, "nlp"
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

        # 🔽 GRÁFICO SÓ EXISTE SE HOUVER CSV
        st.subheader("📊 Distribuição dos riscos")
        contagem_riscos = df_resultado["risco_detectado"].value_counts()
        st.bar_chart(contagem_riscos)

        st.download_button(
            "📥 Baixar resultado",
            df_resultado.to_csv(index=False).encode("utf-8"),
            "resultado_analise_risco.csv",
            "text/csv"
        )

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

        st.download_button(
            label="📥 Baixar resultado",
            data=df_resultado.to_csv(index=False).encode("utf-8"),
            file_name="resultado_analise_risco.csv",
            mime="text/csv"
        )


df_resultado = pd.DataFrame(resultados)
st.subheader("📊 Distribuição dos riscos")

contagem_riscos = df_resultado["risco_detectado"].value_counts()

st.bar_chart(contagem_riscos)
