import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 核心安全配置
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确锁定：黑白极简 (CSS)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .stMarkdown, h1, h2, h3, p, span { color: #000000 !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* 黑色胶囊按钮 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 15px 45px !important;
        border: none !important;
        width: 100%;
        max-width: 320px;
        display: block;
        margin: 0 auto;
        font-weight: bold;
    }

    /* 输入框与上传区 */
    [data-testid="stFileUploader"], .stTextArea textarea {
        background-color: #1A1C1E !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心加固引擎 (STRICT FILTER)
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file):
        if file is None: return None
        try:
            img = Image.open(file)
            img = ImageOps.exif_transpose(img).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode()
        except: return None

    def anti_spoiler_filter(self, stream):
        """
        暴力防御：
        1. 彻底切断 <think> 标签里的碎碎念。
        2. 如果检测到结果数字，直接在流中进行干扰（可选）。
        """
        is_thinking = False
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                if "<think>" in content:
                    is_thinking = True
                    continue
                if "</think>" in content:
                    is_thinking = False
                    continue
                # 只有非思考内容才输出
                if not is_thinking:
                    yield content

engine = EliteEngine(API_KEY)

# =================================================================
# 4. UI 布局
# =================================================================
try:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=110)
    else:
        st.title("MÁXIMOJIHE")
except:
    st.title("MÁXIMOJIHE")

file = st.file_uploader("Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
query = st.text_area("¿Qué duda tienes?", placeholder="Describe tu problema...")

# =================================================================
# 5. 执行逻辑 (FREE MODEL + STRICT PROMPT)
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not file and not query:
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # 识图 (GLM-4V)
            ocr_text = ""
            if file:
                b64 = engine.process_image(file)
                v_res = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "OCR everything."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = v_res.choices[0].message.content

            # 教学 (依然使用免费的 R1)
            # 我们在 Prompt 里加入“角色扮演”压力，让它不敢剧透
            sys_msg = (
                "Eres Máximojihe. Eres un tutor de Eton College. "
                "CRÍTICO: No des el resultado final. Si el problema es 99x100, NUNCA escribas 9900. "
                "Limítate a explicar que 'multiplicar por 100 es añadir dos ceros'. "
                "Termina preguntando: '¿Entonces, cuál sería el número final si le pones los ceros?'."
            )
            
            stream = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", # 维持免费型号
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Problem: {ocr_text}\nQuery: {query}"}
                ],
                stream=True
            )
            
            # 使用暴力过滤器处理流
            st.write_stream(engine.anti_spoiler_filter(stream))

        except Exception as e:
            st.error("Error neuronal.")
            st.code(str(e))

st.markdown("<p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.3</p>", unsafe_allow_html=True)
