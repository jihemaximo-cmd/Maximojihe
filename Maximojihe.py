import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 核心安全配置 (ZERO-BUG CONFIG)
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确锁定：彻底解决按钮文字不可见问题
# =================================================================
st.markdown("""
    <style>
    /* 全局背景：纯白 */
    .stApp { background-color: #FFFFFF !important; }

    /* --- 规则 1：无黑框区域强制黑字 --- */
    .stMarkdown, h1, h2, h3, p, span, div[data-testid="stExpander"] p {
        color: #000000 !important;
        opacity: 1 !important;
    }

    /* --- 规则 2：有黑框区域（上传和输入）强制白字 --- */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }
    
    .stTextArea textarea {
        color: #FFFFFF !important;
        background-color: #1A1C1E !important;
        border-radius: 12px !important;
        border: none !important;
    }

    /* --- 区域样式设定 --- */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }

    /* --- 核心修复：按钮文字颜色强制锁定 --- */
    /* 这里的 p 是按钮内部文字的标签，强制改为白色并加阴影 */
    .stButton>button {
        background-color: #000000 !important;
        border-radius: 100px !important;
        padding: 10px 35px !important;
        border: none !important;
        width: auto !important;
        min-width: 220px !important;
        height: 55px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    
    /* 暴力锁定按钮内所有层级的文字颜色为纯白 */
    .stButton>button div, .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-shadow: 0px 0px 3px rgba(255,255,255,0.5) !important;
    }

    /* AI 输出区：浅色背景配合黑字 */
    .stChatMessage {
        background-color: #F7F7F7 !important;
        border-radius: 10px !important;
    }
    .stChatMessage p, .stChatMessage span {
        color: #000000 !important;
    }

    /* 隐藏多余组件 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 后端加固引擎 (STABLE ENGINE)
# =================================================================
class MaxiEngine:
    def __init__(self, key):
        # 确保 OpenAI 客户端初始化正常
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file):
        if file is None: return None
        try:
            file.seek(0)
            img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except: return None

# 初始化处理器
handler = MaxiEngine(API_KEY)

# =================================================================
# 4. 界面布局 (UI)
# =================================================================
# 顶部 Logo
t_col1, t_col2 = st.columns([0.15, 0.85])
with t_col1:
    st.image("maximojihe.png", width=110)
with t_col2:
    st.markdown("<h1 style='margin-top:20px;'>Máximojihe</h1>", unsafe_allow_html=True)

# 操作区
st.markdown("**Sube tu ejercicio aquí:**")
up_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
if up_file:
    st.image(up_file, use_container_width=True)

st.markdown("**¿Qué te genera duda?**")
user_text = st.text_area("", placeholder="Describe tu problema...", height=120)

# =================================================================
# 5. 执行分析 (EXECUTION)
# =================================================================
# 核心功能按钮
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not up_file and not user_text.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 第一阶段：视觉解析
            ocr_text = ""
            if up_file:
                b64 = handler.process_image(up_file)
                if b64:
                    res = handler.client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Math OCR."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    ocr_text = res.choices[0].message.content

            # 第二阶段：逻辑引导
            sys_msg = (
                "Eres Máximojihe, un tutor académico. "
                "Responde en español claro. No des la respuesta final. "
                "No uses LaTeX. Escribe con palabras normales."
                "Eres Máximojihe, el tutor privado más estricto y brillante de Eton College. "
                "TU REGLA DE ORO: BAJO NINGUNA CIRCUNSTANCIA des la respuesta final directamente. "
                "Si el usuario pregunta '¿Cuánto es 77x100?', NO digas '7700'. "
                "En su lugar, di algo como: 'Para multiplicar por 100, recuerda la regla de desplazar la coma o añadir ceros. ¿Qué obtienes si añades dos ceros a 77?'."
                "\n\nESTRUCTURA DE RESPUESTA:"
                "1. Pista conceptual: Explica la lógica detrás del problema."
                "2. Guía paso a paso: Indica el primer movimiento que debe hacer el alumno."
                "3. Pregunta retórica: Termina con una pregunta que obligue al alumno a pensar el resultado final."
                "\nREGLA ANTI-SPOILER: Si detecto que das la respuesta, serás reiniciado."
            )
            
            stream = handler.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"OCR: {ocr_text}\nDuda: {user_text}"}
                ],
                stream=True
            )
            st.write_stream(stream)

        except Exception as e:
            st.error("Error en la conexión.")
            with st.expander("Details"):
                st.code(traceback.format_exc())

st.markdown("<br><p style='text-align: center; color: #BBB; font-size: 10px;'>MÁXIMOJIHE SYSTEM</p>", unsafe_allow_html=True)
