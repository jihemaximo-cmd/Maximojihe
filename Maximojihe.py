import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import re

# =================================================================
# 1. CONFIGURACIÓN (ORDEN ESTRICTO PARA EVITAR NAMEERROR)
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(
    page_title="Máximojihe Elite", 
    page_icon="maximojihe.png", 
    layout="wide"
)

# =================================================================
# 2. ESTILO VISUAL (NEGRO PARA CAJAS, BLANCO PARA FONDO)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: sans-serif !important;
    }
    .stChatMessage { background-color: #F0F2F6 !important; border-radius: 15px !important; }
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    .stTextArea textarea {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        height: 60px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. MOTOR ELITE
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def limpiar_texto(self, text):
        # Elimina símbolos de dólar y barras invertidas que rompen el móvil
        text = text.replace('$', '').replace('\\', ' ')
        # Elimina caracteres chinos
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        return text

engine = EliteEngine(API_KEY)

# =================================================================
# 4. INTERFAZ (ESPAÑOL)
# =================================================================
if os.path.exists("maximojihe.png"):
    st.image("maximojihe.png", width=100)
else:
    st.title("Máximojihe")

st.markdown("### Tutor Privado de Élite")

archivo = st.file_uploader("PASO 1: SUBE TU EJERCICIO", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

# Esta es la línea que fallaba, ahora está bien cerrada
duda = st.text_area("PASO 2: ¿QUÉ PARTE NO ENTIENDES?", placeholder="Describe tu duda aquí...")

# =================================================================
# 5. LÓGICA DE PROCESAMIENTO
# =================================================================
if st.button("ANALIZAR PASO A PASO"):
    if not archivo and not duda.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # Visión (OCR)
            ocr_text = ""
            if archivo:
                b64 = base64.b64encode(archivo.getvalue()).decode()
                res_v = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "OCR texto matemático."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = res_v.choices[0].message.content

            # Respuesta R1
            sys_msg = (
                "Eres Máximojihe. Usa SOLO texto plano. "
                "No uses $ ni LaTeX. No uses chino. "
                "No des la respuesta final. Guía al alumno en español."
            )
            
            respuesta = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Contexto: {ocr_text}\nDuda: {duda}"}
                ]
            )
            
            contenido = respuesta.choices[0].message.content
            
            # Bloqueo de resultados
            bloqueos = ["6600", "9900", "8800", "7700", "4400"]
            for n in bloqueos:
                if n in contenido:
                    contenido = contenido.split(n)[0] + "\n\n**[Método explicado. ¡Calcula el final tú mismo!]**"
                    break
         
