import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 视觉 CSS (黑玻璃按钮 + 纯白文字修复版) ---
st.markdown("""
    <style>
    /* 核心：高清渲染算法 */
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
        -ms-interpolation-mode: nearest-neighbor !important;
    }

    /* 优化聊天头像 */
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 40px !important;
        height: 40px !important;
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* 页面基础样式 (白底黑字) */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* 黑玻璃上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* --- 🆕 修复：黑玻璃按钮 + 强制白字 --- */
    .stButton>button {
        /* 深黑色玻璃背景 */
        background-color: #1a1a1a !important; 
        background: rgba(20, 20, 20, 0.9) !important;
        backdrop-filter: blur(15px) !important;
        
        /* 强制文字纯白 */
        color: #FFFFFF !important; 
        
        /* 白色细边框，增加对比度 */
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        height: 3.5em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* 确保按钮里的文字（如果是 p 标签）也是白色的 */
    .stButton>button p {
        color: #FFFFFF !important;
    }

    /* 鼠标悬停效果：边框变亮，文字保持白 */
    .stButton>button:hover {
        background: rgba(0, 0, 0, 1) !important; /* 悬停变更黑 */
        color: #FFFFFF !important;
        border-color: #FFFFFF !important; /* 边框全白 */
        transform: translateY(-2px);
    }
    
    /* 点击效果 */
    .stButton>button:active {
        color: #FFFFFF !important;
        background: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 页面头部 ---
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("maximojihe.png", width=65) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Sube tu duda y vamos a resolverla paso a paso.")

# --- 5. 功能区 ---
uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Escribe tu duda:", placeholder="Ej: ¿Cómo empiezo este problema?")

# 按钮区域
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Pon algo para que pueda ayudarte. 😉")
    else:
        with st.spinner("Máximojihe analizando..."):
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
                
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    system_prompt = """
                    Eres Máximojihe, el tutor pro del Eton. 
                    1. NUNCA des el resultado final.
                    2. PROHIBIDO usar LaTeX (\boxed{}).
                    3. Guía paso a paso con palabras claras.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Problema: {context_img} {user_text}. NO des la respuesta final."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Máximojihe")
