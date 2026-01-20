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
                background: rgba(30,41,59,0.92);
                backdrop-filter: blur(12px);
                border-radius: 22px;
                padding: 3rem;
                max-width: 1100px;
                margin-top: 2rem;
            }}

            /* TÍTULO PRINCIPAL */
            div[data-testid="stMark]()

