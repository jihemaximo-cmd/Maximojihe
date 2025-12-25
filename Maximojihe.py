import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re

# =================================================================
# 1. CONFIGURACIÓN
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. CONTROL VISUAL (CSS) - NEGRO PARA CAJAS, BLANCO PARA TEXTO LIBRE
# =================================================================
st.markdown("""
    <style>
    /* 1. Fondo base: Blanco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 2. Áreas sin cuadro: Texto Negro (Títulos, AI y etiquetas) */
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: 'Helvetica', sans-serif !important; 
    }
    
    /* Fondo de mensajes AI suave para contraste */
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 15px !important;
    }

    /* 3. Áreas con cuadro negro: Texto Blanco (Subida e Input) */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }

    .stTextArea textarea {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 15px !important;
        font-size: 16px !important;
        border: none !important;
    }
    .stTextArea textarea::placeholder {
        color: #AAAAAA !important;
    }

    /* 4. Botón: Fondo Negro, Texto Blanco */
    .stButton>button {
        background-color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 100px !important;
        height: 60px !important;
        width: 100% !important;
        max-width: 300px !important;
        display: block !important;
        margin: 0 auto !important;
    }
    .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. MOTOR DE FILTRADO (SIN CHINO, SIN SPOILERS)
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def limpiar_chino(self, text):
        # Elimina cualquier carácter chino
        return re.sub(r'[\u4e00-\u9fff]+', '', text)

    def filtrar_respuesta(self, stream):
        is_thinking = False
        # Lista de bloqueos para evitar que suelte el resultado
        bloqueo = ["6600", "9900", "8800", "7700", "La respuesta es", "Resultado final", "\\boxed"]
        
        texto_acumulado = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                contenido = chunk.choices[0].delta.content
                if "<think>" in contenido:
                    is_thinking = True
                    continue
                if "</think>" in contenido:
                    is_thinking = False
                    continue
                
                if not is_thinking:
                    contenido = self.limpiar_chino(contenido)
                    texto_acumulado += contenido
                    
                    # Si detecta spoiler, corta la transmisión
                    if any(palabra in texto_acumulado for palabra in bloqueo):
                        yield "\n\n**[Concepto explicado. ¡Ahora aplica la regla tú mismo para hallar el número final!]**"
                        break
                    yield contenido

engine = EliteEngine(API_KEY)

# =================================================================
# 4. DISEÑO DE PÁGINA (ESPAÑOL)
# =================================================================
col_logo, col_titulo = st.columns([0.2, 0.8])
with col_logo:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=120)
with col_titulo:
    st.markdown("<h1 style='padding-top:20px;'>Máximojihe Elite</h1>", unsafe_allow_html=True)

st.markdown("---")

# Áreas de entrada
archivo = st.file_uploader("PASO 1: SUBE TU EJERCICIO", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

duda = st.text_area("PASO 2: ¿QUÉ PARTE NO ENTIENDES?", placeholder="Describe tu duda aquí...")

# =================================================================
# 5. EJECUCIÓN
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
                        {"type": "text", "text": "Extrae el texto matemático exactamente."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = res_v.choices[0].message.content

            # Tutoría estricta en Español
            sys_msg = (
                "Eres Máximojihe, un tutor académico de élite. "
                "1. NO uses caracteres chinos. "
                "2. NUNCA des el resultado numérico final. "
                "3. Explica el método y detente antes del último paso. "
                "4. Usa un tono profesional y académico en ESPAÑOL."
            )
            
            stream = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Problema: {ocr_text}\nDuda: {duda}"}
                ],
                stream=True
            )
            
            st.write_stream(engine.filtrar_respuesta(stream))

        except Exception as e:
            st.error("Error del motor neuronal. Inténtalo de nuevo.")

st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.8 • EDICIÓN ESPAÑOL</p>", unsafe_allow_html=True)
