import streamlit as st
from openai import OpenAI
import base64

# --- 1. Configuración de la página ---
st.set_page_config(page_title="Máximo AI", page_icon="🦁")

# --- 2. 终极 CSS：强制显示所有文字，修复输入框隐身 ---
st.markdown("""
    <style>
    /* 强制整体背景白色 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 强制所有基础文字为黑色 */
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* --- 修复输入框 (TextArea) 看不见字的问题 --- */
    /* 强制输入框背景为浅灰色，文字为纯黑色 */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        font-size: 16px !important;
        border: 1px solid #002D62 !important;
    }
    
    /* 修复输入框未点击时的提示文字 (Placeholder) 颜色 */
    .stTextArea textarea::placeholder {
        color: #666666 !important;
    }

    /* --- 黑玻璃上传框效果 --- */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    [data-testid="stFileUploader"] svg { fill: #FFFFFF !important; }

    /* 按钮：Eton 蓝 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold !important;
        height: 3.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Inicialización de API ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. Interfaz ---
st.title("🦁 Máximo AI")
st.write("¡Qué onda! Saca una foto, escribe el problema o pregunta directamente.")

# 功能 A：黑玻璃上传框
uploaded_file = st.file_uploader("1. Sube tu ejercicio (Opcional):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# 功能 B：打字框 (现在强制黑字了)
user_text = st.text_area("2. Escribe aquí el problema o tu duda:", placeholder="Escribe aquí...")

# --- 5. Lógica ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("Escribe algo o sube una foto, porfa. 😉")
    else:
        with st.spinner("Máximo analizando..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("💡 Guía de Máximo")
                
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": "Eres Máximo, tutor fresa de Eton México. No des la respuesta final, guía los pasos en español."},
                        {"role": "user", "content": f"Contexto: {context_img}\nPregunta: {user_text}"}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Academic Honesty")
