import streamlit as st
from openai import OpenAI
import base64

# --- 1. 核心修复：强制显色 CSS ---
st.set_page_config(page_title="Máximo: Eton Study Lab", page_icon="🦁")

st.markdown("""
    <style>
    /* 强制整体背景为白色 */
    .stApp { 
        background-color: #FFFFFF !important; 
    }
    
    /* 强制所有文字内容为深灰色/黑色，防止在深色模式下变白 */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown { 
        color: #1E1E1E !important; 
    }

    /* 修复上传组件的文字颜色 */
    .stFileUploader label div {
        color: #1E1E1E !important;
    }

    /* 按钮：保持 Eton 蓝背景，白色文字 */
    .stButton>button { 
        border-radius: 20px; 
        border: none; 
        background-color: #002D62 !important; 
        color: #FFFFFF !important;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }
    
    /* 输入框和其它组件的边框颜色，增加对比度 */
    .stTextInput>div>div>input {
        color: #1E1E1E !important;
        background-color: #F0F2F6 !important;
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
