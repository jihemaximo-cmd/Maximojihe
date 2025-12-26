import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re

# =================================================================
# 1. CONFIGURACIÓN INICIAL
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. ESTILO VISUAL (CORREGIDO PARA EVITAR ERRORES DE RENDERIZADO)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* Texto libre: Negro */
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: 'Helvetica', sans-serif !important; 
    }
    
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 15px !important;
    }

    /* Cuadros negros con texto blanco */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    .stTextArea textarea {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
    }

    /* Botón cápsula negro */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        height: 60px !important;
        width: 100% !important;
        max-width: 300px !important;
        display: block !important;
        margin: 0 auto !important;
        border: none !important;
    }
    .stButton>button p, .stButton>button span { color: #FFFFFF !important; font-weight: bold; }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. MOTOR ANTIVIRUS (LIMPIEZA DE CHINO, LATEX Y RESULTADOS)
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def clean_output(self, text):
        # 1. Elimina caracteres chinos
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        # 2. Elimina símbolos de dólar que causan el error de SyntaxError/LaTeX
        text = text.replace('$', '')
        return text

    def safe_filter(self, stream):
        is_thinking = False
        # Bloqueamos los números que el modelo suele "soltar"
        spoilers = ["6600", "9900", "8800", "7700", "4400", "Respuesta final", "Resultado"]
        
        full_text = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                
                if "<think>" in content:
                    is_thinking = True
                    continue
                if "</think>" in content:
                    is_thinking = False
                    continue
                
                if not is_thinking:
                    content = self.clean_output(content)
                    full_text += content
                    
                    # Si detecta que va a dar el resultado, corta
                    if any(word in full_text for word in spoilers):
                        yield "\n\n**[Método explicado. ¡Calcula el paso final tú mismo!]**"
                        break
                    yield content

engine = EliteEngine(API_KEY)

# =================================================================
# 4. INTERFAZ
# =================================================================
col_a, col_b = st.columns([0.2, 0.8])
with col_a:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=120)
with col_b:
    st.markdown("<h1 style='padding-top:20px;'>Máximojihe Elite</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("SUBE TU PROBLEMA", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

duda = st.text_area("¿QUÉ TE GENERA DUDA?", placeholder="Ej: No entiendo cómo multiplicar por 100...")

# =================================================================
# 5. LÓGICA DE ANÁLISIS
# =================================================================
if st.button("ANALIZAR SIN SPOILERS"):
    if not archivo and not duda.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # OCR con GLM-4V
            ocr_text = ""
            if archivo:
                b64 = base64.b64encode(archivo.
