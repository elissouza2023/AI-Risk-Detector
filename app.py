import streamlit as st
import pandas as pd
import joblib
import re
import base64
from pathlib import Path

# ======================================================
# CONFIGURAÇÃO INICIAL DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Detector de Risco no Uso de IA em Ambiente Corporativo",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="auto"
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ======================================================
# ESTILIZAÇÃO (Dark mode com bom contraste)
# ======================================================
def aplicar_estilo():
    bg_image = get_base64_image("fundo.jpg")

    st.markdown(
        f"""
        <style>
            /* Fundo com imagem (Cloud-safe) */
            .stApp {{
                background-image:
                    linear-gradient(rgba(15,23,42,0.85), rgba(15,23,42,0.85)),
                    url("data:image/jpg;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            /* Container */
            .block-container {{
                background: rgba(30,41,59,0.9);
                backdrop-filter: blur(12px);
                border-radius: 20px;
                padding: 3rem;
                max-width: 1100px;
                margin-top: 2rem;
            }}

            /* TÍTULO PRINCIPAL */
            div[data-testid="stMarkdownContainer"] h1 {{
                font-size: 3.2rem !important;
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
    Esta ferramenta analisa prompts e identifica riscos relacionados  
    ao uso de Inteligência Artificial em ambientes corporativos,  
    combinando **regras de segurança (Regex)** e **modelo de NLP**.
    """
)

# ======================================================
# CARREGAMENTO DOS MODELOS (cache)
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
    
    # CPF
    if re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', texto):
        return "dado_pessoal"
    
    # Email
    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', texto):
        return "dado_pessoal"
    
    # Palavras de credenciais
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
        return "erro_na_classificacao", "nlp"

# ======================================================
# ANÁLISE DE PROMPT ÚNICO
# ======================================================
st.subheader("✍️ Análise de Prompt Único")

texto_usuario = st.text_area(
    "Cole ou digite o prompt que deseja analisar:",
    height=160,
    placeholder="Exemplo: 'Me envie a senha do sistema financeiro...'"
)

if st.button("🔍 Analisar Prompt", type="primary"):
    if not texto_usuario.strip():
        st.warning("Por favor, digite ou cole algum texto para análise.")
    else:
        risco, metodo = classificar_risco(texto_usuario)
        
        if risco == "baixo_risco":
            st.success(f"✅ Risco: **{risco}** (detectado via {metodo})")
        elif risco == "credencial":
            st.warning(f"⚠️ Risco: **{risco}** (detectado via {metodo})")
        elif risco == "dado_pessoal":
            st.error(f"🚨 Risco: **{risco}** (detectado via {metodo})")
        else:
            st.error(f"🚨 Risco: **{risco}** (detectado via {metodo})")

# ======================================================
# ANÁLISE EM LOTE
# ======================================================
st.subheader("📂 Análise em Lote (CSV)")

arquivo = st.file_uploader(
    "Envie seu arquivo CSV (deve ter a coluna 'text')",
    type=["csv"],
    help="O arquivo precisa ter pelo menos uma coluna chamada 'text'"
)

if arquivo is not None:
    try:
        df = pd.read_csv(arquivo)
        
        if "text" not in df.columns:
            st.error("O arquivo CSV precisa conter a coluna chamada **'text'** (com 't' minúsculo).")
        else:
            with st.spinner("Analisando os prompts..."):
                resultados = []
                for texto in df["text"]:
                    risco, metodo = classificar_risco(str(texto))
                    resultados.append({
                        "texto_original": texto,
                        "risco_detectado": risco,
                        "metodo": metodo
                    })
                
                df_resultado = pd.DataFrame(resultados)
                
                st.success(f"Análise concluída! {len(df_resultado)} prompts processados.")
                st.dataframe(df_resultado, use_container_width=True)
                
                # Distribuição simples
                st.subheader("📊 Distribuição dos Riscos")
                st.bar_chart(df_resultado["risco_detectado"].value_counts())
                
                # Botão de download
                csv = df_resultado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar resultado (CSV)",
                    data=csv,
                    file_name="analise_risco_ia.csv",
                    mime="text/csv"
                )
                
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")

st.markdown("---")
st.caption("Detector de Risco IA v1.0 • Barra Mansa/RJ • 2026")
