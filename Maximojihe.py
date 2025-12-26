import os
import streamlit as st
from openai import OpenAI
import base64
import re

# 1. CONFIGURACIÓN (ORDEN CRÍTICO)
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", layout="wide")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; font-family: sans-serif !important;
    }
    .stChatMessage { background-color: #F0F2F6 !important; border-radius: 15px !important; }
    [data-testid="stFileUploader"] {
        background-color: #000000 !important; border-radius: 20px !important; padding: 15px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    .stTextArea textarea { background-color: #000000 !important; color: #FFFFFF !important; border-radius: 20px !important; }
    .stButton>button {
        background-color: #000000 !important; color: #FFFFFF !important; border-radius: 100px !important;
        height: 60px !important; width: 100% !important; font-weight: bold !important; border: none !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. MOTOR
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)
    def limpiar(self, text):
        text = text.replace('$', '').replace('\\', ' ')
        return re.sub(r'[\u4e00-\u9fff]+', '', text)

engine = EliteEngine(API_KEY)

# 4. INTERFAZ
if os.path.exists("maximojihe.png"):
    st.image("maximojihe.png", width=100)
else:
    st.title("Máximojihe")

st.markdown("### Tutor Privado de Élite")

archivo = st.file_uploader("PASO 1: SUBE TU EJERCICIO", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

duda = st.text_area("PASO 2: ¿QUÉ NO ENTIENDES?", placeholder="Describe tu duda aquí...")

# 5. EJECUCIÓN
if st.button("ANALIZAR PASO A PASO"):
    if not archivo and not duda.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            ocr_text = ""
            if archivo:
                b64 = base64.b64encode(archivo.getvalue()).decode()
                res_v = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [{"type": "text", "text": "OCR."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
                )
                ocr_text = res_v.choices[0].message.content

            res = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": "Eres Máximojihe. Usa texto plano. No des el resultado final. No uses chino. Guía en español."},
                    {"role": "user", "content": f"OCR: {ocr_text}\nDuda: {duda}"}
                ]
            )
            
            cont = res.choices[0].message.content
            bloqueos = ["6600", "9900", "8800", "7700", "4400"]
            for n in bloqueos:
                if n in cont:
                    cont = cont.split(n)[0] + "\n\n**[Calcula el final tú mismo]**"
                    break
            
            st.write(engine.limpiar(cont))
        except Exception as e:
            st.error("Reintenta por favor.")

st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>v7.4 • ESTABLE</p>", unsafe_allow_html=True)
