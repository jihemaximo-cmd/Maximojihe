import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 核心配置 (CORE)
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉加固：深色背景白字 + 浅色背景黑字
# =================================================================
st.markdown("""
    <style>
    /* 基础背景 */
    .stApp { background-color: #FFFFFF !important; }

    /* --- 核心修复：深色容器内的文字强制设为带轮廓的白字 --- */
    [data-testid="stFileUploader"] *, 
    .stTextArea textarea,
    label[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px #000000 !important; /* 增加黑轮廓确保清晰 */
        opacity: 1 !important;
    }

    /* --- 核心修复：输出区域强制设为黑字 --- */
    .stChatMessage p, .stChatMessage span {
        color: #000000 !important;
        text-shadow: none !important;
    }

    /* 上传框：深色圆角矩形 (匹配截屏) */
    [data-testid="stFileUploader"] {
        background-color: #1E1E26 !important;
        border-radius: 25px !important;
        border: 1px solid #333 !important;
        padding: 20px !important;
    }

    /* 输入框：深色圆角矩形 (匹配截屏) */
    .stTextArea textarea {
        background-color: #1E1E26 !important;
        border-radius: 15px !important;
        border: 1px solid #333 !important;
    }

    /* 按钮：左对齐黑色胶囊 + 放大镜 (匹配截屏) */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 10px 40px !important;
        border: none !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        width: auto !important;
        min-width: 240px !important;
        height: 55px !important;
        font-size: 16px !important;
    }
    
    /* 聊天气泡：浅灰色方便阅读黑字 */
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 15px !important;
    }

    /* 隐藏杂质 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 后端稳定引擎 (ENGINE)
# =================================================================
class MaxiAI:
    def __init__(self, key):
        # 修复实例化参数名，确保不报错
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_img(self, file):
        if file is None: return None
        try:
            file.seek(0)
            img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except: return None

# 启动
handler = MaxiAI(API_KEY)

# =================================================================
# 4. 界面布局 (UI)
# =================================================================
# 顶部 Logo 和标题
t_col1, t_col2 = st.columns([0.15, 0.85])
with t_col1:
    st.image("maximojihe.png", width=110)
with t_col2:
    st.markdown("<h1 style='color:black !important; margin-top:20px;'>Máximojihe</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555 !important;'>Tutoría académica profesional.</p>", unsafe_allow_html=True)

st.write("---")

# 上传区
st.markdown("**Sube tu imagen aquí:**")
file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
if file:
    st.image(file, use_container_width=True)

# 输入区
st.markdown("**¿Qué te genera duda?**")
query = st.text_area("", placeholder="Describe el problema aquí...", height=120)

# =================================================================
# 5. 分析执行 (EXECUTION)
# =================================================================
# 按钮文本带放大镜符号 🔍
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not file and not query.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 第一步：识图
            ocr_info = ""
            if file:
                b64 = handler.process_img(file)
                if b64:
                    res = handler.client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Math text extraction."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    ocr_info = res.choices[0].message.content

            # 第二步：解答 (黑字输出)
            sys_p = (
                "Eres Máximojihe, un tutor serio. "
                "No des resultados, solo pasos. "
                "Responde en español. No uses LaTeX ni símbolos raros. "
                "Escribe texto plano para que sea fácil de leer."
            )
            
            stream = handler.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": f"Contexto: {ocr_info}\nDuda: {query}"}
                ],
                stream=True
            )
            st.write_stream(stream)

        except Exception as e:
            st.error("Error en la conexión.")
            with st.expander("Debug"):
                st.code(traceback.format_exc())

st.markdown("<br><p style='text-align:center; color:#AAA; font-size:10px;'>MÁXIMOJIHE PRO</p>", unsafe_allow_html=True)
