import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA (西语界面) ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 视觉 CSS (高清黑玻璃 + 强制白字) ---
st.markdown("""
    <style>
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
    }

    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* Contenedor de subida (Black Glass) */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* Botón Negro Estilo Eton */
    .stButton>button {
        background: rgba(20, 20, 20, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        color: #FFFFFF !important; 
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        height: 3.5em !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }
    .stButton>button p { color: #FFFFFF !important; font-size: 18px !important; }

    .stButton>button:hover {
        background: #000000 !important;
        border-color: #FFFFFF !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API INITIALIZATION ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. INTERFAZ EN ESPAÑOL (页面西语化) ---
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("maximojihe.png", width=65) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Soy tu tutor de lógica. Sube tu ejercicio y razonemos juntos. 🦌")

# 西语提示词
uploaded_file = st.file_uploader("1. Sube la foto de tu problema (JPG/PNG):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Cuéntame tu duda o muestra tu proceso:", placeholder="Ej: ¿Mi lógica es correcta en este paso?")

# --- 5. LÓGICA DE TUTOR (中文回复引导) ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Necesito el problema para poder ayudarte. 😉")
    else:
        with st.spinner("Máximojihe está pensando..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all math text precisely."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # 设定 AI 用中文和你说话，但维持西语导师的灵魂
                    system_prompt = """
                    Eres Máximojihe, un tutor de élite del Eton School. 
                    
                    REGLAS DE ORO:
                    1. NO des la respuesta final. 
                    2. NO uses LaTeX (nada de \\frac, \\sqrt, etc.). Usa lenguaje natural.
                    3. Si el alumno pregunta "¿Está bien?", guía su razonamiento para que él lo verifique.
                    
                    IDIOMA DE RESPUESTA:
                    - Responde SIEMPRE en CHINO (Mandarin) para explicar los conceptos, pero mantén un tono de tutor mexicano 'fresa'.
                    - Usa términos matemáticos claros.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Problema: {context_img}. Duda: {user_text}. 引导学生思考，不给答案。"}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Liderazgo y Honestidad")
