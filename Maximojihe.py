import streamlit as st
from openai import OpenAI
import base64

# --- Configuración de la página (Eton Style) ---
st.set_page_config(page_title="Máximo: Eton Study Lab", page_icon="")

# 强制注入 CSS：确保在任何模式下背景都是白色，文字都是黑色
st.markdown("""
    <style>
    /* 强制背景为白色，文字为深灰色/黑色 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: #1E1E1E !important; }
    
    /* 美化按钮：Eton 蓝 */
    .stButton>button { 
        border-radius: 20px; 
        border: 2px solid #002D62; 
        background-color: #002D62; 
        color: white !important;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover { background-color: #004080; border-color: #004080; }

    /* 让分割线和页脚更清晰 */
    hr { border-top: 1px solid #DDDDDD !important; }
    .stCaption { color: #666666 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Inicialización de API ---
# 这里填你自己的 Key
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- Interfaz en Español (Eton) ---
st.title("🦁 Máximo: Guía de Pensamiento")
st.write("¡Qué onda! Soy **Máximo**. Aquí no venimos a copiar, venimos a entender. Saca una foto de tu ejercicio y armamos la estrategia.")

# 1. Carga de imagen
uploaded_file = st.file_uploader("Sube o toma una foto (ojo ahí, que se vea claro)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Tu ejercicio cargado', use_container_width=True)

    if st.button("🔍 ANALIZAR CON MÁXIMO"):
        with st.spinner("Máximo está pensando... déjame checarlo..."):
            base64_img = encode_image(uploaded_file)

            try:
                # ETAPA 1: GLM-4V (OCR & Visión - GRATIS)
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extrae todo el texto y fórmulas de esta imagen. No resuelvas nada."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                question_text = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("📝 Guía de Estrategia")

                # ETAPA 2: DeepSeek-R1 (Pensamiento Lógico - GRATIS)
                system_prompt = """
                Eres 'Máximo', un tutor de élite del Eton School en la CDMX. Tu estilo es 'fresa', inteligente y motivador.
                Tu misión es guiar al estudiante usando el método socrático.
                
                【REGLAS DE MÁXIMO】
                1. NUNCA des la respuesta final ni resultados numéricos.
                2. Usa modismos de CDMX educados (fresa): 'Ojo aquí', 'No manches', 'Está súper sencillo', 'Fíjate bien'.
                3. Si te piden la respuesta, niégate con humor: 'Híjole, así no aprendes nada. Mejor piénsale conmigo'.
                
                【ESTRUCTURA】
                - Concepto: ¿De qué trata el tema?
                - Pista Pro: El truco para no fallar.
                - Empujoncito: La primera parte del planteamiento.
                """

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"El texto del ejercicio es: {question_text}. Ayúdame a entenderlo pero no me des la respuesta final."}
                    ],
                    stream=True
                )

                # Mostrar el razonamiento en tiempo real
                st.write_stream(response)

            except Exception as e:
                st.error(f"Híjole, algo salió mal: {e}")

st.markdown("---")
st.caption("🇲🇽 Exclusivo para Eton School | Honor Code: Honestidad Académica")
