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

# --- 5. MOTOR DE RAZONAMIENTO REFORZADO (加固版) ---
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Sube una imagen o escribe algo. 😉")
    else:
        with st.spinner("Máximojihe razonando..."):
            try:
                # 1. 强制重置图片流，防止读取失败
                uploaded_file.seek(0) 
                b64_img = process_image(uploaded_file)
                
                # 2. 强化 OCR 指令：命令它必须描述出数学逻辑
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Identify and transcribe ALL mathematical expressions in this image. Do not say you cannot see it."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                )
                context_img = ocr_res.choices[0].message.content

                # 3. 这里的 System Prompt 是灵魂，防止它说中文
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    sys_prompt = """
                    Eres Máximojihe, el tutor de élite del Eton School. 
                    TU MISIÓN: Guiar al alumno paso a paso EXCLUSIVAMENTE en ESPAÑOL.
                    
                    REGLAS DE ORO:
                    1. PROHIBIDO EL CHINO: Bajo ninguna circunstancia uses caracteres chinos.
                    2. PROHIBIDO DAR LA RESPUESTA: Solo da los pasos lógicos.
                    3. SI NO VES LA IMAGEN: No te rindas. Usa el texto que el alumno escribió para deducir el problema.
                    4. FORMATO: Usa puntos claros. No uses LaTeX.
                    """

                    # 强制加入当前环境提示
                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": f"Contexto de la imagen (OCR): {context_img}. Duda del alumno: {user_text}. Responde solo en español y guíame."}
                        ],
                        stream=True
                    )
                    st.write_stream(response)
            except Exception as e:
                st.error(f"Error crítico: {e}")
