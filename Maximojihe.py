import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import datetime
import traceback
import sys

# =================================================================
# 1. IDENTIDAD DEL PROYECTO (MAXI'S LEGACY)
# =================================================================
VERSION = "3.5.0-MAXI-GENIUS"
AUTHOR = "Maxi (CTO de 10 años)" # 你的专属头衔
GLOBAL_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"

st.set_page_config(
    page_title=f"Máximojihe by Maxi",
    page_icon="maximojihe.png",
    layout="centered"
)

# =================================================================
# 2. SISTEMA VISUAL DE ALTO CONTRASTE (MAXI STYLE)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    /* 强制所有文字为黑色，绝对不准隐形 */
    .stMarkdown, p, span, li, label, h1, h2, h3 { 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    /* 黑色 Eton 上传器 */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 40px !important;
        border: 2px solid #333 !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    /* 黑色 Eton 尊享按钮 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        height: 4.5em !important;
        width: 100%;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. MOTOR LÓGICO (修复了之前的 TypeError)
# =================================================================
class EtonAIEngine:
    """
    Clase maestra de IA diseñada por Maxi.
    """
    def __init__(self, key_input):
        # 核心修复：确保 key 被正确存入 client
        self.api_key = key_input
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url="https://api.siliconflow.cn/v1"
        )

    def prepare_image(self, uploaded_file):
        """防止 NoneType 报错的图片处理逻辑"""
        if uploaded_file is None: return None
        try:
            uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            img = ImageOps.exif_transpose(img).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            st.error(f"Error de imagen: {e}")
            return None

    def run_ocr(self, b64):
        """视觉专家识别"""
        try:
            res = self.client.chat.completions.create(
                model="THUDM/GLM-4.1V-9B-Thinking",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "Extract all math notation. No extra talk."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}]
            )
            return res.choices[0].message.content
        except: return "No image context."

# --- 实例化引擎 (这次绝对不会报错了！) ---
# 修复点：直接传入变量，不使用错误的参数名调用
engine = EtonAIEngine(GLOBAL_KEY)

# =================================================================
# 4. INTERFAZ DE USUARIO (UI)
# =================================================================
st.title(f"🦌 Máximojihe")
st.write(f"Desarrollado por **{AUTHOR}**")

doc = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if doc: st.image(doc, use_container_width=True)

query = st.text_area("2. Tu duda específica:", placeholder="Ej: No entiendo este logaritmo...")

# =================================================================
# 5. RAZONAMIENTO ACADÉMICO
# =================================================================
if st.button("🔍 INICIAR ANÁLISIS"):
    if not doc and not query.strip():
        st.warning("⚠️ Sube algo para que Maxi pueda procesarlo.")
    else:
        with st.spinner("Razonando con la mente de un genio..."):
            try:
                ocr_data = ""
                if doc:
                    b64_data = engine.prepare_image(doc)
                    if b64_data:
                        ocr_data = engine.run_ocr(b64_data)

                st.divider()
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # 专属 Maxi 的系统指令
                    sys_prompt = f"""
                    Eres Máximojihe, el mentor de Eton. 
                    Trabajas para el CTO Maxi, un genio de 10 años.
                    - IDIOMA: Español (MX). Prohibido chino.
                    - NO LATEX: Escribe todo en palabras claras.
                    - GUÍA: No des la respuesta final, solo pasos.
                    """
                    
                    stream = engine.client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": f"Contexto: {ocr_data}. Duda: {query}."}
                        ],
                        stream=True
                    )
                    st.write_stream(stream)
            except Exception as e:
                st.error("Error crítico de sistema.")
                st.code(traceback.format_exc())

# 页脚：天才认证
st.markdown("---")
st.caption(f"© 2025 Eton School | Made by Maxi (Maximojihe--la inteligencia artificial que te ayuda.)")
