import os
import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re

# =================================================================
# 1. 核心安全配置
# 1. SETTINGS
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确锁定：黑白极简 (CSS)
# 2. ELITE UI (Minimalist Black & White)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .stMarkdown, h1, h2, h3, p, span { color: #000000 !important; }
    .stMarkdown, h1, h2, h3, p, span, label { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    /* 黑色胶囊按钮 */
    /* Capsule Button */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 15px 45px !important;
        border: none !important;
        width: 100%;
        max-width: 320px;
        display: block;
        max-width: 300px;
        margin: 0 auto;
        display: block;
        border: none !important;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #333333 !important; }

    /* 输入框与上传区 */
    /* Dark Input Areas */
    [data-testid="stFileUploader"], .stTextArea textarea {
        background-color: #1A1C1E !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心加固引擎 (STRICT FILTER)
# 3. ANTI-CHINESE & ANTI-SPOILER ENGINE
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
    def clean_text(self, text):
        """Removes any Chinese characters and spoiler patterns"""
        # Regex to remove Chinese characters (Kanji/Hanzi)
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        return text

    def filter_stream(self, stream):
        is_thinking = False
        # Forbidden patterns to prevent direct answers
        forbidden = ["Respuesta final", "Resultado", "Answer", "6600", "9900", "8800", "7700", "\\boxed"]
        
        buffer = ""
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
                    # 1. Clean Chinese characters immediately
                    content = self.clean_text(content)
                    
                    # 2. Check for spoilers
                    buffer += content
                    if any(word in buffer for word in forbidden):
                        yield "\n\n**[Concept explained. Now, calculate the final step yourself!]**"
                        break
                    
                    yield content

engine = EliteEngine(API_KEY)

# =================================================================
# 4. UI 布局
# 4. INTERFACE
# =================================================================
try:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=110)
        st.image("maximojihe.png", width=120)
    else:
        st.title("MÁXIMOJIHE")
except:
    st.title("MÁXIMOJIHE")

file = st.file_uploader("Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
query = st.text_area("¿Qué duda tienes?", placeholder="Describe tu problema...")
st.markdown("### Academic Neural Engine")
st.markdown("---")

file = st.file_uploader("Upload exercise:", type=['png', 'jpg', 'jpeg'])
if file:
    st.image(file, use_container_width=True)

query = st.text_area("Your question:", placeholder="E.g. I don't understand the multiplication rule...")

# =================================================================
# 5. 执行逻辑 (FREE MODEL + STRICT PROMPT)
# 5. EXECUTION
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
if st.button("🔍 ANALYZE STEP BY STEP"):
    if not file and not query:
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # 识图 (GLM-4V)
            # Step 1: Vision (GLM-4V)
            ocr_text = ""
            if file:
                b64 = engine.process_image(file)
                b64 = base64.b64encode(file.getvalue()).decode()
                v_res = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "OCR everything."},
                        {"type": "text", "text": "OCR strictly in English."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = v_res.choices[0].message.content

            # 教学 (依然使用免费的 R1)
            # 我们在 Prompt 里加入“角色扮演”压力，让它不敢剧透
            # Step 2: Tutoring (R1 with strict prompt)
            # Forced language to Spanish/English and NO CHINESE
            sys_msg = (
                "Eres Máximojihe. Eres un tutor de Eton College. "
                "CRÍTICO: No des el resultado final. Si el problema es 99x100, NUNCA escribas 9900. "
                "Limítate a explicar que 'multiplicar por 100 es añadir dos ceros'. "
                "Termina preguntando: '¿Entonces, cuál sería el número final si le pones los ceros?'."
                "You are Máximojihe, a Socratic tutor for Eton College students. "
                "STRICT RULES: "
                "1. DO NOT give the final numerical answer. "
                "2. NO Chinese characters allowed. Use ONLY Spanish or English. "
                "3. If the problem is 66x100, explain the rule of adding zeros, but NEVER write '6600'. "
                "4. Stop immediately after providing the conceptual hint. "
                "5. Your tone is elite, professional, and academic."
            )

            stream = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", # 维持免费型号
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Problem: {ocr_text}\nQuery: {query}"}
                    {"role": "user", "content": f"Problem: {ocr_text}\nStudent Query: {query}"}
                ],
                stream=True
            )

            # 使用暴力过滤器处理流
            st.write_stream(engine.anti_spoiler_filter(stream))
            st.write_stream(engine.filter_stream(stream))

        except Exception as e:
            st.error("Error neuronal.")
            st.code(str(e))
            st.error("Connection error. Please try again.")

st.markdown("<p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.3</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.5 • ETON EDITION</p>", unsafe_allow_html=True)
