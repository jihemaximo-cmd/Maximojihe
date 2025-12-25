import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", # 浏览器标签页图标
    layout="centered"
)

# --- 2. 视觉 CSS 优化 (高清渲染 + 界面样式) ---
st.markdown("""
    <style>
    /* 强制图片高清渲染，防止缩放模糊 */
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
    }

    /* 页面背景白色 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 文字颜色 */
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* 黑玻璃效果上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        padding: 25px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 聊天头像高清化 */
    [data-testid="stChatMessageAvatarAssistant"] img {
        width: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
    }

    /* Eton 蓝按钮 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        height: 3.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面布局 ---
# 使用 st.columns 优化顶部 LOGO 显示，防止拉伸
col1, col2 = st.columns([0.15, 0.85])
with col1:
    # 这里的 width=60 是为了在保持清晰度的同时控制大小
    st.image("maximojihe.png", width=60) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Sube tu duda. Aquí razonamos como cracks.")

# 上传
uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# 输入
user_text = st.text_area("2. Escribe tu duda aquí:", placeholder="Ej: No entiendo este paso...")

# --- 5. 核心逻辑 (AI 回复头像) ---
if st.button("🔍 CONSULTAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Pon algo para que pueda ayudarte. 😉")
    else:
        with st.spinner("Máximojihe está pensando..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                
                # 聊天消息头像使用本地高清原图
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    system_prompt = """
                    Eres Máximojihe, el tutor pro del Eton CDMX. 
                    REGLAS:
                    1. NUNCA des el resultado final.
                    2. PROHIBIDO usar LaTeX (\boxed{}).
                    3. Guía paso a paso con palabras.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Contexto: {context_img}. Duda: {user_text}. NO des la respuesta."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Máximojihe")
