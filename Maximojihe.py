import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered" # 保持中心布局，让图片最大化显示
)

# --- 2. 视觉修复 CSS (确保不遮挡，图片完整) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* 解决图片显示不全的问题 */
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        border-radius: 15px;
        border: 1px solid #EEE;
    }

    /* 黑玻璃上传框 - 优化边距防止重叠 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.98) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin-bottom: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 黑色按钮 */
    .stButton>button {
        background: #000000 !important;
        color: #FFFFFF !important; 
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        height: 3.8em !important;
        width: 100%;
        margin-top: 20px;
    }
    .stButton>button p { color: #FFFFFF !important; font-size: 18px !important; }
    
    /* 输入框文字颜色修复 */
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API INITIALIZATION ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 简洁交互界面 ---
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("maximojihe.png", width=70) 
with col2:
    st.title("Máximojihe: Tutor de Élite")

st.write("Sube tu duda. Mi honor es enseñarte, nunca darte la respuesta final. 🦌")

# 步骤 1: 上传图片
uploaded_file = st.file_uploader("1. Sube tu ejercicio aquí:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    # 强制图片完整展示，解决“看不见”的问题
    st.image(uploaded_file, use_container_width=True)

# 步骤 2: 输入问题
user_text = st.text_area("2. ¿Qué parte te causa duda?", placeholder="Describe lo que no entiendes...")

# --- 5. 核心 AI 逻辑 (严禁答案 + 纯西语) ---
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Necesito ver el problema primero. 😉")
    else:
        with st.spinner("Máximojihe razonando..."):
            try:
                context_img = ""
                if uploaded_file:
                    # 重新编码图片以确保 OCR 准确
                    uploaded_file.seek(0)
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all math text accurately."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()

                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # 加固的严师指令
                    system_prompt = """
                    Eres Máximojihe, el tutor más pro del Eton School. 
                    
                    REGLAS DE ORO ABSOLUTAS:
                    1. IDIOMA: Responde ÚNICAMENTE en ESPAÑOL (México).
                    2. PROHIBIDO DAR RESPUESTAS: Tienes TERMINANTEMENTE PROHIBIDO dar el resultado final (ej: No digas 12, no digas 31.01).
                    3. SOLO GUÍA LÓGICA: Explica el concepto y el siguiente paso. Si el alumno pregunta '¿Cuál es el resultado?', dile que tu honor de Eton te impide ser una calculadora.
                    4. NO LATEX: Explica las fórmulas con palabras sencillas (ej: 'x al cuadrado', 'dividido por').
                    5. ACTITUD: Eres brillante, motivador y un poco estricto.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Problema: {context_img}. Duda: {user_text}. Guíame con lógica en español, PERO NO ME DES NINGÚN RESULTADO NUMÉRICO FINAL."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Excelencia Académica")
