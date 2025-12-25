import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. 4K VISUAL CSS (Black Glass + White Text) ---
st.markdown("""
    <style>
    img { image-rendering: -webkit-optimize-contrast !important; image-rendering: crisp-edges !important; }
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* Black Glass Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* Botón Negro Eton */
    .stButton>button {
        background: rgba(20, 20, 20, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        color: #FFFFFF !important; 
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        height: 3.5em !important;
        width: 100%;
    }
    .stButton>button p { color: #FFFFFF !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API INITIALIZATION ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. INTERFAZ EN ESPAÑOL ---
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("maximojihe.png", width=65) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Soy tu tutor del Eton School. Sube tu duda y razonemos juntos. 🦌")

uploaded_file = st.file_uploader("1. Sube la foto de tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Cuéntame qué parte no entiendes:", placeholder="Ej: No sé cómo empezar...")

# --- 5. LÓGICA DE TUTOR (STRICT SPANISH & NO ANSWERS) ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Necesito ver el problema primero. 😉")
    else:
        with st.spinner("Máximojihe razonando..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all math text."}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # ⚠️ 这里的指令确保 AI 导师只说西语，且只给步骤不给答案
                    system_prompt = """
                    Eres Máximojihe, el tutor más pro del Eton School. 
                    
                    TUS REGLAS DE ORO:
                    1. IDIOMA: Responde ÚNICAMENTE en ESPAÑOL (México).
                    2. NO RESPUESTAS: Tienes PROHIBIDO dar el resultado final (ej: x=2).
                    3. SOLO PASOS: Explica la lógica paso a paso para que el alumno llegue solo a la solución.
                    4. NO LATEX: No uses símbolos como \\frac o \\sqrt. Escribe 'dividido por' o 'raíz cuadrada'.
                    5. ACTITUD: Eres un mentor motivador y brillante.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Problema: {context_img}. Duda: {user_text}. Guíame paso a paso en español sin dar la respuesta."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Excelencia Académica")
