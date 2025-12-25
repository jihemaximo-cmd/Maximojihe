import streamlit as st
from openai import OpenAI
import base64

# --- 1. 核心修复：强制显色 CSS ---
st.markdown("""
    <style>
    /* 1. 强制整页背景和基础文字 */
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, div, label { color: #1e1e1e !important; }

    /* 2. 专门修复那个看不见的上传框 (File Uploader) */
    /* 强制上传框背景变浅灰色，防止它变成全黑 */
    [data-testid="stFileUploader"] {
        background-color: #f8f9fb !important;
        padding: 10px;
        border-radius: 10px;
    }
    
    /* 强制上传框里的所有文字（Drag and drop 等）变成深色 */
    [data-testid="stFileUploader"] section div div {
        color: #1e1e1e !important;
    }
    
    /* 强制上传框的小图标也变色 */
    [data-testid="stFileUploader"] svg {
        fill: #1e1e1e !important;
    }

    /* 3. 修复底部的按钮文字颜色 */
    .stButton>button {
        background-color: #002d62 !important;
        color: white !important;
        border: none !important;
    }
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
