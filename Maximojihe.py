import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 4K 极清视觉优化 CSS ---
st.markdown("""
    <style>
    /* 核心：高清渲染算法 */
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
        -ms-interpolation-mode: nearest-neighbor !important;
    }

    /* 优化聊天头像：增加像素密度感 */
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 40px !important;
        height: 40px !important;
        border: 1px solid rgba(0,0,0,0.05); /* 极细边框增加精致感 */
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* 页面基础样式 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* 黑玻璃上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 按钮：Eton 蓝色 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #003d85 !important;
        transform: scale(1.02);
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
    # 针对 4K 屏幕，手动控制显示宽度
    st.image("maximojihe.png", width=65) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Sube tu duda y vamos a resolverla paso a paso.")

# --- 5. 功能区 ---
uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Escribe tu duda:", placeholder="Ej: ¿Cómo empiezo este problema?")

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
                
                # 聊天头像使用高清原图
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
