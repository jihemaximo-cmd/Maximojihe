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
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
    }

    /* Estilo de la App */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* Contenedor de subida de archivos (Black Glass) */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* Botón Negro con Letras Blancas Clear */
    .stButton>button {
        background-color: #000000 !important; 
        background: rgba(20, 20, 20, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        color: #FFFFFF !important; /* LETRAS BLANCAS */
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        height: 3.5em !important;
        width: 100%;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }

    .stButton>button p { color: #FFFFFF !important; font-size: 18px !important; }

    .stButton>button:hover {
        background: #000000 !important;
        border-color: #FFFFFF !important;
        transform: translateY(-2px);
    }

    /* Input text area */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API INITIALIZATION ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. INTERFAZ ---
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("maximojihe.png", width=65) 
with col2:
    st.title("Máximojihe")

st.write("¡Qué onda! Sube tu ejercicio. No esperes la respuesta, espera el conocimiento. 🦌")

uploaded_file = st.file_uploader("1. Sube tu foto aquí:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. ¿Qué parte te está costando?", placeholder="Ej: No sé cómo simplificar el logaritmo...")

# --- 5. LÓGICA DE TUTOR ELITISTA (PROHIBIDO RESPUESTAS) ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Sube algo primero, no soy adivino. 😉")
    else:
        with st.spinner("Máximojihe analizando tu potencial..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all math text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # PROMPT REFORZADO PARA EVITAR LO QUE PASÓ ARRIBA
                    system_prompt = """
                    Eres Máximojihe, el tutor más inteligente y fresa del Eton School en CDMX.
                    TU MISIÓN: Ayudar al alumno a razonar, NUNCA darle la respuesta final.
                    
                    REGLAS INQUEBRANTABLES:
                    1. Si el resultado es 1/(1-x^2), PROHIBIDO escribirlo. 
                    2. Si el alumno te da la respuesta, no le digas 'Correcto', dile 'Vas por buen camino, ¿cómo llegaste ahí?'.
                    3. PROHIBIDO USAR LATEX. No uses \, {, }, frac, boxed, o sqrt.
                    4. Usa lenguaje humano: 'raíz cuadrada', 'entre', 'derivada de lo de adentro'.
                    5. Sé motivador, usa frases como 'Tú puedes, crack', 'Eso es de genios'.
                    6. Si detectas que el alumno solo quiere copiar, dile que en el Eton se forman líderes, no copiadoras.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Contexto del problema: {context_img}. Duda del alumno: {user_text}. Guíame paso a paso pero OCULTA el resultado final."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | Honestidad Académica")
