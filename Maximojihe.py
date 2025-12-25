import streamlit as st
from openai import OpenAI
import base64

# --- 页面配置 ---
st.set_page_config(page_title="Máximo: Eton Study Lab", page_icon="🦁")

# --- 核心视觉：黑色包围白色 ---
st.markdown("""
    <style>
    /* 1. 外层背景：纯黑色包围 */
    .stApp {
        background-color: #000000 !important;
    }

    /* 2. 中间内容区：变回白色卡片，增加边距 */
    [data-testid="stMainViewContainer"] > section > div {
        background-color: #FFFFFF !important;
        padding: 30px !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
        margin-top: 20px !important;
        margin-bottom: 20px !important;
    }

    /* 3. 强制内容文字显示为黑色 */
    h1, h2, h3, p, span, label, div {
        color: #1E1E1E !important;
    }

    /* 4. 上传框：浅灰色背景，黑色虚线 */
    [data-testid="stFileUploader"] section {
        background-color: #F8F9FB !important;
        border: 2px dashed #002D62 !important;
    }
    
    /* 上传框里的文字也强制黑色 */
    [data-testid="stFileUploader"] * {
        color: #1E1E1E !important;
    }

    /* 5. 按钮：Eton 蓝底白字 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        height: 3.5em !important;
    }

    /* 修复分割线颜色 */
    hr { border-top: 1px solid #DDDDDD !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 以下代码保持不变 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("🦁 Máximo AI")
st.write("¡Qué onda! Soy **Máximo**. Aquí tienes tu zona de entrenamiento. Saca una foto y vamos a darle.")

uploaded_file = st.file_uploader("Sube tu ejercicio aquí:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Tu ejercicio', use_container_width=True)

    if st.button("🔍 ANALIZAR CON MÁXIMO"):
        with st.spinner("Pensando..."):
            # ... (后续的识别和推理逻辑代码和之前一样)
            base64_img = encode_image(uploaded_file)
            try:
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [{"type": "text", "text": "Extrae el texto de esta imagen."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                )
                question_text = ocr_res.choices[0].message.content
                st.divider()
                st.subheader("📝 Estrategia")
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[{"role": "system", "content": "Eres Máximo, tutor fresa de Eton. No des respuestas, guía."}, {"role": "user", "content": f"Texto: {question_text}"}],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Academic Honesty")
