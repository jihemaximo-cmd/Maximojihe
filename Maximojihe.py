import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re

# =================================================================
# 1. SETTINGS
# 1. CONFIGURACIÓN
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 精确视觉控制 (CSS)
# 2. CONTROL VISUAL (CSS) - NEGRO PARA CAJAS, BLANCO PARA TEXTO LIBRE
# =================================================================
st.markdown("""
    <style>
    /* 1. 基础背景：纯白 */
    /* 1. Fondo base: Blanco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 2. 无框区域：强制黑字 (包括 AI 回复和所有标题) */
    /* 2. Áreas sin cuadro: Texto Negro (Títulos, AI y etiquetas) */
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: 'Helvetica', sans-serif !important; 
    }
    
    /* AI 聊天气泡背景调浅，确保黑字清晰 */
    /* Fondo de mensajes AI suave para contraste */
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 15px !important;
    }

    /* 3. 有黑框区域：强制黑底白字 (上传框和输入框) */
    /* 3. Áreas con cuadro negro: Texto Blanco (Subida e Input) */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }
    /* 暴力锁定黑框内的文字为白色 */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }
@@ -54,12 +53,11 @@
        font-size: 16px !important;
        border: none !important;
    }
    /* 修正输入框提示词颜色 */
    .stTextArea textarea::placeholder {
        color: #AAAAAA !important;
    }

    /* 4. 按钮：黑底白字 */
    /* 4. Botón: Fondo Negro, Texto Blanco */
    .stButton>button {
        background-color: #000000 !important;
        border: 2px solid #000000 !important;
@@ -80,111 +78,112 @@
        border-color: #333333 !important;
    }

    /* 隐藏多余组件 */
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心逻辑引擎
# 3. MOTOR DE FILTRADO (SIN CHINO, SIN SPOILERS)
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def clean_text(self, text):
        # 实时移除中文字符
    def limpiar_chino(self, text):
        # Elimina cualquier carácter chino
        return re.sub(r'[\u4e00-\u9fff]+', '', text)

    def filter_stream(self, stream):
    def filtrar_respuesta(self, stream):
        is_thinking = False
        # 熔断词库
        forbidden = ["6600", "9900", "8800", "7700", "Answer is", "Respuesta final", "\\boxed"]
        # Lista de bloqueos para evitar que suelte el resultado
        bloqueo = ["6600", "9900", "8800", "7700", "La respuesta es", "Resultado final", "\\boxed"]

        full_output = ""
        texto_acumulado = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                if "<think>" in content:
                contenido = chunk.choices[0].delta.content
                if "<think>" in contenido:
                    is_thinking = True
                    continue
                if "</think>" in content:
                if "</think>" in contenido:
                    is_thinking = False
                    continue

                if not is_thinking:
                    content = self.clean_text(content)
                    full_output += content
                    contenido = self.limpiar_chino(contenido)
                    texto_acumulado += contenido

                    # 检查是否触碰剧透红线
                    if any(word in full_output for word in forbidden):
                        yield "\n\n**[Concept provided. Now apply the rule to find the final number!]**"
                    # Si detecta spoiler, corta la transmisión
                    if any(palabra in texto_acumulado for palabra in bloqueo):
                        yield "\n\n**[Concepto explicado. ¡Ahora aplica la regla tú mismo para hallar el número final!]**"
                        break
                    yield content
                    yield contenido

engine = EliteEngine(API_KEY)

# =================================================================
# 4. UI 布局
# 4. DISEÑO DE PÁGINA (ESPAÑOL)
# =================================================================
t_col1, t_col2 = st.columns([0.2, 0.8])
with t_col1:
col_logo, col_titulo = st.columns([0.2, 0.8])
with col_logo:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=120)
with t_col2:
with col_titulo:
    st.markdown("<h1 style='padding-top:20px;'>Máximojihe Elite</h1>", unsafe_allow_html=True)

st.markdown("---")

# 有框区域 1
file = st.file_uploader("STEP 1: SUBMIT EXERCISE", type=['png', 'jpg', 'jpeg'])
if file:
    st.image(file, use_container_width=True)
# Áreas de entrada
archivo = st.file_uploader("PASO 1: SUBE TU EJERCICIO", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

# 有框区域 2
query = st.text_area("STEP 2: WHAT IS YOUR DOUBT?", placeholder="Describe the part you don't understand...")
duda = st.text_area("PASO 2: ¿QUÉ PARTE NO ENTIENDES?", placeholder="Describe tu duda aquí...")

# =================================================================
# 5. 执行分析
# 5. EJECUCIÓN
# =================================================================
if st.button("ANALYZE STEP BY STEP"):
    if not file and not query:
if st.button("ANALIZAR PASO A PASO"):
    if not archivo and not duda.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # Visión (OCR)
            ocr_text = ""
            if file:
                b64 = base64.b64encode(file.getvalue()).decode()
                v_res = engine.client.chat.completions.create(
            if archivo:
                b64 = base64.b64encode(archivo.getvalue()).decode()
                res_v = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "OCR strictly in English."},
                        {"type": "text", "text": "Extrae el texto matemático exactamente."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = v_res.choices[0].message.content
                ocr_text = res_v.choices[0].message.content

            # Tutoría estricta en Español
            sys_msg = (
                "You are Máximojihe, an elite academic tutor. "
                "1. NO Chinese characters. "
                "2. NEVER give the final numerical answer. "
                "3. Stop before the last step. "
                "4. Professional tone."
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
                    {"role": "user", "content": f"OCR: {ocr_text}\nQuery: {query}"}
                    {"role": "user", "content": f"Problema: {ocr_text}\nDuda: {duda}"}
                ],
                stream=True
            )

            st.write_stream(engine.filter_stream(stream))
            st.write_stream(engine.filtrar_respuesta(stream))

        except Exception as e:
            st.error("Engine reset. Please try again.")
            st.error("Error del motor neuronal. Inténtalo de nuevo.")

st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.7</p>", unsafe_allow_html=True)
st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.8 • EDICIÓN ESPAÑOL</p>", unsafe_allow_html=True)
