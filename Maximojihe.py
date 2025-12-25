import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE ÉLITE ---
st.set_page_config(
    page_title="Máximojihe Tutor Pro", 
    page_icon="maximojihe.png", 
    layout="centered"
)

# --- 2. CSS AVANZADO (Contraste Máximo y Visibilidad) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* Forzar visibilidad de texto del chat */
    .stChatMessage { background-color: #F0F2F6 !important; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .stChatMessage p, .stChatMessage span, .stChatMessage li { 
        color: #000000 !important; 
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* Imagen completa sin recortes */
    [data-testid="stImage"] img {
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        width: 100% !important;
    }

    /* Black Glass Uploader Profesional */
    [data-testid="stFileUploader"] {
        background: #121212 !important;
        border: 2px dashed #444 !important;
        border-radius: 20px !important;
        padding: 2rem !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* Botón Eton con Efecto Hover */
    .stButton>button {
        background: #000000 !important;
        color: #FFFFFF !important; 
        border: 1px solid #333 !important;
        border-radius: 40px !important;
        font-weight: 800 !important;
        height: 4em !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #333333 !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Títulos y etiquetas */
    h1, h2, label { color: #111111 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DE API Y PROCESAMIENTO ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def process_image(uploaded_file):
    """Codifica la imagen y la prepara para OCR"""
    try:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode('utf-8')
    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return None

# --- 4. INTERFAZ DE USUARIO ---
col1, col2 = st.columns([0.18, 0.82])
with col1:
    st.image("maximojihe.png", width=75) 
with col2:
    st.title("Máximojihe: Tutor de Élite")

st.info("Recordatorio: Mi misión es guiarte paso a paso. No pidas la respuesta final, pues mi honor no me permite dártela. 🦌")

# Espacio de trabajo
uploaded_file = st.file_uploader("1. Sube la evidencia de tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, caption="Problema detectado")

user_text = st.text_area("2. Cuéntame tu duda específica:", height=100, placeholder="Ej: ¿Qué propiedad de logaritmos debo usar aquí?")

# --- 5. MOTOR DE RAZONAMIENTO REFORZADO ---
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not uploaded_file and not user_text:
        st.warning("Por favor, proporciona una imagen o una duda escrita. 😉")
    else:
        with st.spinner("Máximojihe está conectando con el conocimiento..."):
            try:
                # PASO A: OCR DETALLADO
                context_img = "No hay imagen disponible."
                if uploaded_file:
                    b64_img = process_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": "Extract and describe all mathematical symbols and text. Be precise."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()

                # PASO B: RESPUESTA DEL TUTOR
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    # Instrucciones de blindaje total
                    sys_prompt = """
                    Eres Máximojihe, tutor del Eton School.
                    TU FILOSOFÍA: Guía socrática. Ayuda al alumno a pensar.
                    
                    REGLAS INQUEBRANTABLES:
                    1. IDIOMA: Solo Español Mexicano fluido. NUNCA uses chino ni inglés.
                    2. ANTI-RESPUESTA: No des valores numéricos finales. Si el problema es x+2=4, no digas x=2. Di 'resta 2 en ambos lados'.
                    3. FORMATO: Texto plano claro. PROHIBIDO LaTeX (no \, no {}, no frac). Usa 'dividido por', 'raiz de', etc.
                    4. VISIBILIDAD: Usa listas con puntos para separar los pasos.
                    5. RESPONSABILIDAD: Si la imagen está incompleta, descríbelo y pregunta al alumno.
                    """

                    full_prompt = f"Contexto matemático: {context_img}. Duda del alumno: {user_text}."
                    
                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": full_prompt}
                        ],
                        stream=True
                    )
                    st.write_stream(response)

            except Exception as e:
                st.error(f"Hubo un inconveniente en la conexión: {str(e)}")

st.markdown("---")
st.caption("© 2025 Eton School - Departamento de Matemáticas | Excelencia y Honor")
