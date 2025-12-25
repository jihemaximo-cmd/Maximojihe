import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import re

# =================================================================
# 1. 核心修复：彻底禁用公式渲染，防止手机端崩溃
# =================================================================
# 必须在最开头，强制不处理任何数学语法
st.set_page_config(
    page_title="Máximojihe Elite", 
    page_icon="maximojihe.png", 
    layout="wide"
)

# =================================================================
# 2. 视觉控制 (黑白极简)
# =================================================================
st.markdown("""
    <style>
    /* 强制所有文字为纯文本，防止浏览器尝试渲染公式 */
    .stApp { background-color: #FFFFFF !important; }
    
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: sans-serif !important;
    }
    
    .stChatMessage { background-color: #F0F2F6 !important; border-radius: 15px !important; }

    /* 有框区域 */
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

    /* 黑色大按钮 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        height: 60px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心逻辑
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def clean_text(self, text):
        # 强制删掉所有可能触发数学渲染的符号
        text = text.replace('$', '').replace('\\', ' ')
        # 删掉中文
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        return text

engine = EliteEngine("sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl")
BASE_URL = "https://api.siliconflow.cn/v1"

# =================================================================
# 4. 界面 (全部西班牙语)
# =================================================================
if os.path.exists("maximojihe.png"):
    st.image("maximojihe.png", width=100)
else:
    st.title("Máximojihe")

st.markdown("### Tutor Privado de Élite")

archivo = st.file_uploader("SUBE TU EJERCICIO", type=['png', 'jpg', 'jpeg'])
if archivo:
    st.image(archivo, use_container_width=True)

duda = st.text_area("¿QUÉ PARTE NO ENTIENDES?", placeholder="Describe tu duda aquí...")

# =================================================================
# 5. 执行逻辑
# =================================================================
if st.button("ANALIZAR PASO A PASO"):
    if not archivo and not duda.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # 识图
            ocr_text = ""
            if archivo:
                b64 = base64.b64encode(archivo.getvalue()).decode()
                v_res = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Extract text, no math symbols."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = v_res.choices[0].message.content

            # 教学逻辑
            # 使用 st.text 替代 st.markdown 是一种极端但有效的防崩溃手段
            # 但这里我们先尝试过滤后的 markdown
            sys_msg = (
                "Eres Máximojihe. Usa SOLO texto plano. "
                "No uses $, no uses LaTeX. No uses chino. "
                "No des la respuesta final. Guía paso a paso."
            )
            
            res = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Contexto: {ocr_text}\nDuda: {duda}"}
                ]
            )
            
            final_text = engine.clean_text(res.choices[0].message.content)
            st.write(final_text) # st.write 比 st.markdown 更不容易触发公式 Bug

        except Exception as e:
            st.error("Error de conexión.")

st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>v7.1 • COMPATIBILIDAD MÓVIL</p>", unsafe_allow_html=True)
