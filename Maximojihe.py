import streamlit as st
from openai import OpenAI
import base64

# --- 1. Configuración de la página (Eton Style) ---
st.set_page_config(page_title="Máximo AI", page_icon="🦁")

# --- 2. CSS: Mantener el diseño "Blanco con Negro Glass" ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, div { color: #1E1E1E !important; }

    /* Caja de carga "Black Glass" */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    [data-testid="stFileUploader"] svg { fill: #FFFFFF !important; }

    /* Área de texto y botones */
    .stTextArea>div>div>textarea { background-color: #F0F2F6 !important; color: #1E1E1E !important; }
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold !important;
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
st.write("¡Qué onda! Saca una foto, escribe el problema o simplemente pregunta.")

# 功能 A：上传图片（可选）
uploaded_file = st.file_uploader("1. Sube tu ejercicio (Opcional):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# 功能 B：纯文字输入（手抄题目或对话）
user_text = st.text_area("2. Escribe aquí el problema o tu duda:", placeholder="Ej: ¿Cómo se resuelve esta ecuación? o 'Copia aquí tu ejercicio'...")

# --- 5. Lógica de Respuesta ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    # 检查是否既没传图也没打字
    if not uploaded_file and not user_text:
        st.warning("Oye, escribe algo o sube una foto para poder ayudarte. 😉")
    else:
        with st.spinner("Máximo analizando..."):
            try:
                context_from_img = ""
                
                # 情况 1：如果有图片，先识别图片内容
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_from_img = ocr_res.choices[0].message.content

                # 情况 2：不论有没有图，都把 user_text 传给 DeepSeek 进行逻辑引导
                st.divider()
                st.subheader("💡 Guía de Máximo")
                
                # 构建发送给 AI 的最终提示词
                prompt_content = f"Contexto de imagen: {context_from_img}\nPregunta/Texto del alumno: {user_text}"

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": "Eres Máximo, tutor fresa de Eton México. Ayuda al alumno con su duda de forma lógica. NO des la respuesta final, solo guía paso a paso en español."},
                        {"role": "user", "content": prompt_content}
                    ],
                    stream=True
                )
                st.write_stream(response)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Honor Code")
