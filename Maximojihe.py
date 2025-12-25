import streamlit as st
from openai import OpenAI
import base64

# --- 1. 核心修复：强制显色 CSS ---
st.markdown("""
    <style>
    /* 1. 全局暴力清零：强制所有背景白，所有文字黑 */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: white !important;
        color: #1E1E1E !important;
    }

    /* 2. 彻底修复上传框：强制背景色和边框颜色 */
    [data-testid="stFileUploader"] section {
        background-color: #F8F9FB !important;
        border: 2px dashed #002D62 !important;
        color: #1E1E1E !important;
    }

    /* 3. 强制上传框内的所有文字变黑（包括那个 Browse files 按钮） */
    [data-testid="stFileUploader"] * {
        color: #1E1E1E !important;
    }

    /* 4. 按钮样式：强制 Eton 蓝底白字 */
    .stButton>button {
        background-color: #002D62 !important;
        color: white !important;
        border-radius: 20px !important;
    }

    /* 5. 隐藏 Streamlit 右上角的小红点和菜单，减少干扰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 API ---
# 使用你在截图里显示的那个免费 Key
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 3. 界面内容 (全西语) ---
st.title("🦁 Máximo: Guía de Pensamiento")
st.write("¡Qué onda! Soy **Máximo**. Saca una foto de tu ejercicio y armamos la estrategia. **No doy respuestas, te enseño a ganar.**")

uploaded_file = st.file_uploader("Sube tu ejercicio aquí:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Tu ejercicio', use_container_width=True)

    if st.button("🔍 ANALIZAR CON MÁXIMO"):
        with st.spinner("Máximo está analizando..."):
            base64_img = encode_image(uploaded_file)
            try:
                # 眼睛：GLM-4V 识图
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extrae el texto de esta imagen. No resuelvas."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                question_text = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("📝 Estrategia de Máximo")

                # 大脑：DeepSeek-R1 引导
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": "Eres Máximo, un tutor fresa de Eton México. No des respuestas, solo guía."},
                        {"role": "user", "content": f"Texto: {question_text}\nAyúdame a entenderlo."}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Academic Honesty")
