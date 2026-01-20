import streamlit as st
import pandas as pd
import joblib
import re
import base64

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Detector de Risco no Uso de IA em Ambiente Corporativo",
    page_icon="🔐",
    layout="centered"
)

# ======================================================
# FUNÇÃO PARA CARREGAR IMAGEM EM BASE64 (Streamlit Cloud)
# ======================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# ======================================================
# ESTILO VISUAL (Cloud-safe)
# ======================================================
def aplicar_estilo():
    bg_image = get_base64_image("fundo.jpg")

    st.markdown(
        f"""
        <style>
            /* Fundo da aplicação */
            .stApp {{
                background-image:
                    linear-gradient(rgba(15,23,42,0.88), rgba(15,23,42,0.88)),
                    url("data:image/jpg;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            /* Container principal */
           .block-container {{
                background-color: #0f172a;
                border-radius: 22px;
                padding: 3rem;
                max-width: 1100px;
                margin-top: 2rem;
            }}


            /* TÍTULO PRINCIPAL */
            div[data-testid="stMarkdownContainer"] h1 {{
                font-size: 3rem !important;
                font-weight: 700 !important;
                text-align: center;
                color: #60a5fa !important;
            }}

            /* SUBTÍTULOS */
            div[data-testid="stMarkdownContainer"] h2 {{
                font-size: 2.1rem !important;
                font-weight: 600 !important;
                color: #93c5fd !important;
                margin-top: 2.5rem;
            }}

            /* Labels */
            label {{
                font-size: 1.1rem !important;
                color: #e5e7eb !important;
            }}
            p, span, label {{
                color: #e5e7eb !important;
            }}
            div[data-testid="stMarkdownContainer"] h2 {{
                color: #eab308 !important;
            }}

            /* Botão Analisar Prompt */
            .stButton > button {{
                background-color: #FFDEAD !important;
                color: #1e293b !important; /* texto escuro para contraste */
                border: none;
                border-radius: 10px;
                padding: 0.75rem 1.8rem;
                font-size: 1.1rem;
                font-weight: 600;
            }}

            /* Efeito hover */
            .stButton > button:hover {{
                background-color: #FFA500 !important;
                color: #1e293b !important;
            }}


        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilo()

# ======================================================
# TÍTULO E DESCRIÇÃO
# ======================================================
st.title("🔐 Detector de Risco no Uso de IA")

st.markdown(
    """
    Esta ferramenta analisa prompts e identifica riscos relacionados ao uso de Inteligência Artificial em ambientes corporativos, combinando **regras de segurança (Regex)** e **modelo de NLP**."""
)

# ======================================================
# CARREGAMENTO DOS MODELOS
# ======================================================
@st.cache_resource
def carregar_modelos():
    try:
        model = joblib.load("modelo_risco_ia.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
        return model, vectorizer
    except Exception as e:
        st.error(f"Erro ao carregar modelos: {str(e)}")
        return None, None

model, vectorizer = carregar_modelos()

if model is None or vectorizer is None:
    st.stop()

# ======================================================
# DETECÇÃO POR REGEX
# ======================================================
def detectar_risco_regex(texto):
    if not texto or not isinstance(texto, str):
        return "baixo_risco"

    texto = texto.lower()

    if re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', texto):
        return "dado_pessoal"

    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', texto):
        return "dado_pessoal"

    if re.search(r'\b(senha|password|token|api ?key|credencial|chave secreta)\b', texto):
        return "credencial"

    return "baixo_risco"

# ======================================================
# CLASSIFICAÇÃO FINAL
# ======================================================
def classificar_risco(texto):
    risco_regex = detectar_risco_regex(texto)
    if risco_regex != "baixo_risco":
        return risco_regex, "regex"

    try:
        texto_vec = vectorizer.transform([texto])
        risco_nlp = model.predict(texto_vec)[0]
        return risco_nlp, "nlp"
    except:
        return "erro", "nlp"

# ======================================================
# BADGE DE RISCO (MELHORIA 1)
# ======================================================
def badge_risco(risco, metodo):
    cores = {
        "baixo_risco": "#22c55e",
        "credencial": "#f59e0b",
        "dado_pessoal": "#ef4444"
    }

    icones = {
        "baixo_risco": "✅",
        "credencial": "⚠️",
        "dado_pessoal": "🚨"
    }

    textos = {
        "baixo_risco": "Nenhum risco relevante identificado",
        "credencial": "Possível exposição de credenciais",
        "dado_pessoal": "Exposição de dados pessoais (LGPD)"
    }

    cor = cores.get(risco, "#64748b")
    icone = icones.get(risco, "❓")
    texto = textos.get(risco, "Risco não classificado")

    st.markdown(
        f"""
        <div style="
            background-color: {cor}22;
            border-left: 6px solid {cor};
            padding: 1.3rem 1.6rem;
            border-radius: 14px;
            margin-top: 1.5rem;
            font-size: 1.15rem;
            font-weight: 600;
        ">
            {icone} <b>{texto}</b><br>
            <span style="font-size: 0.95rem; opacity: 0.85;">
                Método de detecção: {metodo.upper()}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# ANÁLISE DE PROMPT ÚNICO
# ======================================================
st.subheader("✍️ Análise de Prompt Único")

texto_usuario = st.text_area(
    "Cole ou digite o prompt que deseja analisar:",
    height=160,
    placeholder="Exemplo: Me envie a senha do sistema financeiro"
)

if st.button("🔍 Analisar Prompt"):
    if not texto_usuario.strip():
        st.warning("Por favor, digite ou cole algum texto para análise.")
    else:
        risco, metodo = classificar_risco(texto_usuario)
        badge_risco(risco, metodo)

# ======================================================
# ANÁLISE EM LOTE
# ======================================================
st.subheader("📂 Análise em Lote (CSV)")

arquivo = st.file_uploader(
    "Envie seu arquivo CSV (deve ter a coluna 'text')",
    type=["csv"]
)

if arquivo is not None:
    try:
        df = pd.read_csv(arquivo)

        if "text" not in df.columns:
            st.error("O CSV precisa conter a coluna 'text'")
        else:
            resultados = []
            for texto in df["text"]:
                risco, metodo = classificar_risco(str(texto))
                resultados.append({
                    "texto": texto,
                    "risco": risco,
                    "metodo": metodo
                })

            df_resultado = pd.DataFrame(resultados)

            st.success("Análise concluída com sucesso!")
            st.dataframe(df_resultado, use_container_width=True)

            st.subheader("📊 Distribuição dos Riscos")
            st.bar_chart(df_resultado["risco"].value_counts())

            csv = df_resultado.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Baixar resultado (CSV)",
                csv,
                "analise_risco_ia.csv",
                "text/csv"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")

st.markdown("---")
st.caption("Detector de Risco IA v1.0 • Barra Mansa/RJ • 2026")

