import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA (网页标签页图标) ---
# 确保你 GitHub 里的文件名确实是 maximojihe.png
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 视觉 CSS (白底黑字 + 黑玻璃) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* 黑玻璃上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        padding: 25px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 输入框样式 */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
    }

    /* Eton 蓝按钮 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    /* 隐藏头像旁的默认样式 */
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面布局 ---
# 用 st.columns 让标题和鹿头并排显示
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("maximojihe.png", width=50) # 标题旁也放一个鹿
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Sube tu duda. Aquí razonamos como cracks.")

uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Escribe tu duda aquí:", placeholder="Ej: No entiendo este paso...")

# --- 5. 核心逻辑 (AI 回复头像换成鹿) ---
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
                
                # --- 这里是关键：avatar 参数直接用你的图片文件名 ---
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    system_prompt = """
                    Eres Máximojihe, el tutor pro del Eton. 
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
st.caption("🇲🇽 Eton School | Máximojihe")
