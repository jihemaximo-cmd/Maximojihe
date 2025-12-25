import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 核心架构配置
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确锁定：有黑框=白字，无黑框=黑字
# =================================================================
st.markdown("""
    <style>
    /* 全局强制白底 */
    .stApp { background-color: #FFFFFF !important; }

    /* --- 区域 A: 白色背景区 (无黑框) -> 强制黑字 --- */
    .stMarkdown, h1, h2, h3, p, span {
        color: #000000 !important;
        opacity: 1 !important;
    }

    /* --- 区域 B: 深色背景区 (有黑框) -> 强制白字 --- */
    /* 包含上传器内部文字和输入框内部文字 */
    [data-testid="stFileUploader"] *, 
    .stTextArea textarea {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    /* --- 样式还原：深色容器 --- */
    /* 上传框：深色圆角矩形 */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 25px !important;
    }

    /* 输入框：深色圆角矩形 */
    .stTextArea textarea {
        background-color: #1A1C1E !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 15px !important;
    }

    /* 按钮：左对齐黑色胶囊 + 放大镜图标 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 10px 35px !important;
        border: none !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        width: auto !important;
        min-width: 220px !important;
        height: 52px !important;
    }

    /* --- 区域 C: AI 输出区 (浅灰色背景) -> 强制黑字 --- */
    .stChatMessage {
        background-color: #F7F7F7 !important;
        border-radius: 10px !important;
        margin-top: 15px !important;
    }
    .stChatMessage p, .stChatMessage span {
        color: #000000 !important;
    }

    /* 隐藏杂项 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 稳健后端引擎 (STABLE ENGINE)
# =================================================================
class MaxiCore:
    def __init__(self, key):
        # 修复实例化参数，确保 API 调用链路通畅
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file):
        """确保图片能够被正确读取并转换为 Base64"""
        if file is None: return None
        try:
            file.seek(0)
            img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except: return None

# 实例化
handler = MaxiCore(API_KEY)

# =================================================================
# 4. 界面排版 (UI LAYOUT)
# =================================================================
# 顶部 Logo
st.write("")
col_l, col_m, col_r = st.columns([0.15, 0.7, 0.15])
with col_l:
    st.image("maximojihe.png", width=110)
with col_m:
    st.markdown("<h1 style='margin-top:20px;'>Máximojihe</h1>", unsafe_allow_html=True)

# 功能区
st.write("")
st.markdown("**Sube tu ejercicio aquí:**")
uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="main_up")

if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

st.write("")
st.markdown("**¿Qué te genera duda?**")
user_query = st.text_area("", placeholder="Describe tu problema aquí...", height=120, key="main_text")

# =================================================================
# 5. 执行分析 (EXECUTION)
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not uploaded_file and not user_query.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 识图步骤
            context = ""
            if uploaded_file:
                b64 = handler.process_image(uploaded_file)
                if b64:
                    res = handler.client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Extract math text accurately."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    context = res.choices[0].message.content

            # 引导步骤 (输出黑字)
            sys_inst = (
                "Eres Máximojihe, un tutor académico profesional. "
                "Responde en español claro. No uses chino. "
                "No des resultados directos, guía paso a paso. "
                "No uses LaTeX. Escribe texto plano fácil de leer."
            )
            
            stream = handler.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_inst},
                    {"role": "user", "content": f"Contexto: {context}\nDuda: {user_query}"}
                ],
                stream=True
            )
            st.write_stream(stream)

        except Exception as e:
            st.error("Error técnico en la consulta.")
            with st.expander("Ver detalle"):
                st.code(traceback.format_exc())

# 页脚
st.markdown("<br><p style='text-align: center; color: #BBB; font-size: 10px;'>MÁXIMOJIHE ACADEMIC ENGINE</p>", unsafe_allow_html=True)
