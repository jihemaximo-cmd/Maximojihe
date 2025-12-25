import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Máximojihe", page_icon="maximojihe.png", layout="wide") # 换成宽屏模式看得更清

# --- 2. ELITE CSS (强制图片完整显示) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    /* 确保图片 100% 宽度显示，绝不裁剪 */
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        border: 2px solid #000;
        border-radius: 10px;
    }
    [data-testid="stFileUploader"] { background: #1E1E1E !important; border-radius: 20px; padding: 20px; }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    .stButton>button { background: #000 !important; color: #FFF !important; border-radius: 30px; width: 100%; height: 3.5em; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API CORE (这里已经包含 API 了) ---
client = OpenAI(
    api_key="sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl", 
    base_url="https://api.siliconflow.cn/v1"
)

def encode_img(file): return base64.b64encode(file.read()).decode('utf-8')

# --- 4. INTERFACE ---
col1, col2 = st.columns([0.1, 0.9])
with col1: st.image("maximojihe.png")
with col2: st.title("Máximojihe: Tutor de Élite")

st.write("Sube tu ejercicio. Mi misión es tu aprendizaje, no darte la respuesta. 🦌")

# 增加一列布局，让图片显示的区域更大
up_file = st.file_uploader("Sube tu imagen aquí:", type=['png', 'jpg', 'jpeg'])
if up_file:
    st.image(up_file, use_container_width=True) # 这里是关键：铺满容器宽度

u_text = st.text_area("¿Qué te genera duda?", placeholder="Describe lo que ves si la imagen no es clara...")

# --- 5. 终极指令：死也不给答案 ---
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not up_file and not u_text: st.warning("Sube algo primero.")
    else:
        with st.spinner("Máximojihe analizando..."):
            ctx = ""
            if up_file:
                # 强化 OCR 指令，要求描述细节
                res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking", 
                    messages=[{"role": "user", "content": [{"type": "text", "text": "Transcribe every detail. If text is missing or blurry, explain the mathematical context."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_img(up_file)}"}}]}] 
                )
                ctx = res.choices[0].message.content
            
            with st.chat_message("assistant", avatar="maximojihe.png"):
                # 这里的指令被我加固成了“绝对禁令”
                sys = """
                Eres Máximojihe. Responde SIEMPRE en ESPAÑOL.
                REGLA DE ORO: Tienes PROHIBIDO dar números finales o soluciones resueltas. 
                Si el alumno pregunta por la respuesta, dile que tu honor de Eton no te lo permite.
                Solo puedes dar la 'receta' (pasos), nunca el 'plato cocinado' (resultado).
                No uses LaTeX.
                """
                stream = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", 
                    messages=[
                        {"role": "system", "content": sys}, 
                        {"role": "user", "content": f"Problema: {ctx}. Duda: {u_text}. Guíame con lógica sin dar el resultado."}
                    ], 
                    stream=True
                )
                st.write_stream(stream)
