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
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 精确视觉控制 (CSS)
# =================================================================
st.markdown("""
    <style>
    /* 1. 基础背景：纯白 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 2. 无框区域：强制黑字 (包括 AI 回复和所有标题) */
    .stMarkdown, h1, h2, h3, p, span, label, .stChatMessage { 
        color: #000000 !important; 
        font-family: 'Helvetica', sans-serif !important; 
    }
    
    /* AI 聊天气泡背景调浅，确保黑字清晰 */
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 15px !important;
    }

    /* 3. 有黑框区域：强制黑底白字 (上传框和输入框) */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }
    /* 暴力锁定黑框内的文字为白色 */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }

    .stTextArea textarea {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 15px !important;
        font-size: 16px !important;
        border: none !important;
    }
    /* 修正输入框提示词颜色 */
    .stTextArea textarea::placeholder {
        color: #AAAAAA !important;
    }

    /* 4. 按钮：黑底白字 */
    .stButton>button {
        background-color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 100px !important;
        height: 60px !important;
        width: 100% !important;
        max-width: 300px !important;
        display: block !important;
        margin: 0 auto !important;
    }
    .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }

    /* 隐藏多余组件 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心逻辑引擎
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def clean_text(self, text):
        # 实时移除中文字符
        return re.sub(r'[\u4e00-\u9fff]+', '', text)

    def filter_stream(self, stream):
        is_thinking = False
        # 熔断词库
        forbidden = ["6600", "9900", "8800", "7700", "Answer is", "Respuesta final", "\\boxed"]
        
        full_output = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                if "<think>" in content:
                    is_thinking = True
                    continue
                if "</think>" in content:
                    is_thinking = False
                    continue
                
                if not is_thinking:
                    content = self.clean_text(content)
                    full_output += content
                    
                    # 检查是否触碰剧透红线
                    if any(word in full_output for word in forbidden):
                        yield "\n\n**[Concept provided. Now apply the rule to find the final number!]**"
                        break
                    yield content

engine = EliteEngine(API_KEY)

# =================================================================
# 4. UI 布局
# =================================================================
t_col1, t_col2 = st.columns([0.2, 0.8])
with t_col1:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=120)
with t_col2:
    st.markdown("<h1 style='padding-top:20px;'>Máximojihe Elite</h1>", unsafe_allow_html=True)

st.markdown("---")

# 有框区域 1
file = st.file_uploader("STEP 1: SUBMIT EXERCISE", type=['png', 'jpg', 'jpeg'])
if file:
    st.image(file, use_container_width=True)

# 有框区域 2
query = st.text_area("STEP 2: WHAT IS YOUR DOUBT?", placeholder="Describe the part you don't understand...")

# =================================================================
# 5. 执行分析
# =================================================================
if st.button("ANALYZE STEP BY STEP"):
    if not file and not query:
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            ocr_text = ""
            if file:
                b64 = base64.b64encode(file.getvalue()).decode()
                v_res = engine.client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "OCR strictly in English."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                ocr_text = v_res.choices[0].message.content

            sys_msg = (
                "You are Máximojihe, an elite academic tutor. "
                "1. NO Chinese characters. "
                "2. NEVER give the final numerical answer. "
                "3. Stop before the last step. "
                "4. Professional tone."
            )
            
            stream = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"OCR: {ocr_text}\nQuery: {query}"}
                ],
                stream=True
            )
            
            st.write_stream(engine.filter_stream(stream))

        except Exception as e:
            st.error("Engine reset. Please try again.")

st.markdown("<br><p style='text-align:center; color:#CCC; font-size:10px;'>MAXIMOJIHE ELITE v6.7</p>", unsafe_allow_html=True)
