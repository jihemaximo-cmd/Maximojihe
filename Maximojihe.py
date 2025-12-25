import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# 确保你仓库里有 logo.png
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 视觉 CSS (白底黑字 + 黑玻璃 + 对话框优化) ---
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

    /* 按钮：Eton 蓝 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面布局 ---
st.title("🦁 Máximojihe")
st.write("¡Qué onda! Sube tu duda. Aquí no solo damos respuestas, construimos genios.")

# 上传区
uploaded_file = st.file_uploader("1. Sube tu ejercicio (Opcional):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# 输入区
user_text = st.text_area("2. Escribe tu duda aquí:", placeholder="Ej: No entiendo cómo simplificar esto...")

# --- 5. 核心逻辑 (聊天图标替换在此) ---
if st.button("🔍 CONSULTAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Necesito una foto o texto para ayudarte. 😉")
    else:
        with st.spinner("Máximojihe está pensando..."):
            try:
                # 识图逻辑
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                
                # --- 关键修改：使用鹿头图标显示回复 ---
                with st.chat_message("assistant", avatar="maximojihe.png"): 
                    st.subheader("💡 Guía de Máximojihe")
                    
                    system_prompt = """
                    Eres Máximojihe, el tutor más pro del Eton en CDMX.
                    REGLAS CRÍTICAS:
                    1. NUNCA des el resultado final.
                    2. PROHIBIDO usar LaTeX o símbolos raros (\boxed).
                    3. Guía paso a paso con palabras claras y estilo 'fresa'.
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
                st.error(f"Híjole, algo falló: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Máximojihe")
