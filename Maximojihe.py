import streamlit as st
from openai import OpenAI
import base64

# --- 1. 页面设置 ---
st.set_page_config(page_title="Máximo AI", page_icon="🦁")

# --- 2. 核心视觉：白底黑字 + 黑玻璃上传框 ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, div { color: #1E1E1E !important; }

    /* 黑玻璃上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    [data-testid="stFileUploader"] svg { fill: #FFFFFF !important; }

    /* 提问输入框样式优化 */
    .stTextInput>div>div>input {
        background-color: #F0F2F6 !important;
        color: #1E1E1E !important;
        border-radius: 10px !important;
    }

    /* 按钮：Eton 蓝 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 API ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面展示 ---
st.title("🦁 Máximo AI")
st.write("¡Qué onda! Saca una foto de tu duda y dime qué parte te cuesta más.")

# 功能 A：上传图片 (黑玻璃效果)
uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, use_container_width=True)
    
    # 功能 B：添加具体问题输入框
    user_question = st.text_input("2. ¿Qué parte no entiendes? (Opcional)", placeholder="Ej: No entiendo el paso 2...")

    if st.button("🔍 ANALIZAR CON MÁXIMO"):
        with st.spinner("Máximo analizando..."):
            base64_img = encode_image(uploaded_file)
            try:
                # 步骤 1：后台静默识别图片内容
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{"role": "user", "content": [{"type": "text", "text": "Extract text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                )
                context_text = ocr_res.choices[0].message.content

                # 步骤 2：结合图片内容 + 学生的问题进行引导
                st.divider()
                st.subheader("💡 Estrategia de Máximo")
                
                final_prompt = f"Problema en imagen: {context_text}\nPregunta específica del alumno: {user_question if user_question else 'Guíame en este ejercicio'}"

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": "Eres Máximo, tutor fresa de Eton México. No des la respuesta final. Responde específicamente a lo que el alumno pregunta sobre el ejercicio, usando pistas lógicas."},
                        {"role": "user", "content": final_prompt}
                    ],
                    stream=True
                )
                st.write_stream(response)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Honor Code: Honestidad Académica")
