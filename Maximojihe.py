import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 核心安全配置 (ZERO-BUG CONFIG)
# =================================================================
# 确保 API 参数名与 OpenAI 库完全对齐，杜绝 TypeError
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确对齐 (VISUAL LOGIC)
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

    /* --- 规则 2：有黑框区域强制白字 --- */
    /* 针对上传组件内部文字 */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }
    
    /* 针对输入框内部文字 */
    .stTextArea textarea {
        color: #FFFFFF !important;
        background-color: #1A1C1E !important;
        border-radius: 12px !important;
        border: none !important;
    }

    /* --- 区域样式设定 --- */
    /* 上传框：深色圆角容器 */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }

    /* 按钮：圆角胶囊黑色背景 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 10px 35px !important;
        border: none !important;
        font-weight: bold !important;
        width: auto !important;
        min-width: 200px !important;
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
        # 实例化时确保参数名正确，解决 133 行报错
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file):
        """处理上传图片，包含指针安全重置"""
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
# 顶部 Logo 展示
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
# 使用放大镜符号模拟你的截图样式
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

            # 第二阶段：逻辑引导 (输出纯黑字)
            sys_msg = (
                "Eres Máximojihe, un tutor académico. "
                "Responde en español claro. No des la respuesta final. "
                "No uses LaTeX. Escribe con palabras normales."
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
