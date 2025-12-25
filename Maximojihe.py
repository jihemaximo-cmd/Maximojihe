import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# 把 page_icon 设置为你的图片文件名
st.set_page_config(
    page_title="Máximojihe", 
    page_icon="https://lh3.googleusercontent.com/gg-dl/ABS2GSlWTwxoJ3i6yCNz784pGxVWw5wjXwftjZd6t39fIoXSRHLFm5vXf7XlXXsbgLesUtOCo3y0EGKZBKwOEY6nl-9EA5bxlopvl662EcUbKuNU4fN-c844M36Cq5LWuALYrmCdI9OzJiGmPxY51sdMeP8mSQ49LNrglx8Jyu9Hzd0QVCpq=s1024-rj",  # 这里填入你上传的图片文件名
    layout="centered"
)
# --- 2. CSS INTEGRADO: BLANCO, NEGRO GLASS Y TEXTO LEGIBLE ---
st.markdown("""
    <style>
    /* Fondo de página blanco y texto negro */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* Caja de carga estilo Black Glass */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    [data-testid="stFileUploader"] svg { fill: #FFFFFF !important; }

    /* Input de texto (TextArea) corregido */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        font-size: 16px !important;
        border: 1px solid #002D62 !important;
    }

    /* Botón estilo Eton */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold !important;
        height: 3.5em !important;
        border: none !important;
    }

    /* Ocultar elementos innecesarios */
    [data-testid="stImageCaption"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE API ---
# Usando tu clave de SiliconFlow (Free Tier)
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. INTERFAZ DE USUARIO ---
st.title("🦁 Máximo AI")
st.write("¡Qué onda! Saca una foto, escribe tu ejercicio o solo pregunta. **Aquí aprendes, no solo copias.**")

# A. Zona de Imagen (Opcional)
uploaded_file = st.file_uploader("1. Sube o toma una foto (Black Glass Zone):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# B. Zona de Texto (Opcional / Chat)
user_text = st.text_area("2. Escribe el problema o tu duda aquí:", placeholder="Ej: No entiendo cómo despejar X...")

# --- 5. LÓGICA DE RESPUESTA DE MÁXIMO ---
if st.button("🔍 CONSULTAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("Oye, dame algo con qué trabajar. Sube una foto o escribe algo. 😉")
    else:
        with st.spinner("Máximo está analizando tu duda..."):
            try:
                # Paso 1: Visión silenciosa (si hay imagen)
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                # Paso 2: Razonamiento de Máximo (DeepSeek-R1)
                st.divider()
                st.subheader("💡 Estrategia de Máximo")

                # PROMPT DE ELITE: No respuestas, no símbolos raros
                system_prompt = """
                Eres Máximo, el tutor más pro del Eton en CDMX. Hablas con estilo 'fresa', inteligente y motivador.
                
                REGLAS CRÍTICAS:
                1. NUNCA des el resultado numérico o respuesta final. Si te piden 99*98, no digas 9702.
                2. NUNCA uses símbolos de código o LaTeX (nada de \\times, \\boxed, \\theta, etc.). Escribe como en WhatsApp.
                3. Usa lenguaje humano: 'por', 'dividido entre', 'elevado a'.
                4. Estructura: Explica el concepto brevemente, da un truco lógico y deja que el alumno haga el último paso.
                """

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Contexto imagen: {context_img}. Duda del alumno: {user_text}. ¡Recuerda no dar la respuesta!"}
                    ],
                    stream=True
                )
                
                # Mostrar respuesta en vivo
                st.write_stream(response)

            except Exception as e:
                st.error(f"Híjole, algo falló: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School Pride | No Answers, Just Logic")
