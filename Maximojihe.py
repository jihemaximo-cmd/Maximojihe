import streamlit as st
from openai import OpenAI
import base64

# --- 1. 图标硬编码逻辑 (将你的鹿头图片转为代码) ---
# 这是一个小巧的编码图标，确保标签页不再是地球或狮子
def set_favicon():
    # 这是一个通用的数学/教育类图标的Base64，确保它显示为一个独特的蓝色标识
    # 如果你有特定的 logo.jpg，请确保它在 GitHub 根目录，代码会自动读取
    try:
        with open("logo.jpg", "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/jpeg;base64,{data}"
    except:
        return "🔷" # 如果找不到文件，先用这个蓝色方块占位，比狮子专业

# --- 2. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Máximojihe", 
    page_icon=set_favicon(), 
    layout="centered"
)

# --- 3. 视觉 CSS (白底黑字 + 黑玻璃) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E1E1E !important; }

    /* 黑玻璃上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 修复输入框文字 */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        font-size: 16px !important;
    }

    /* Eton 蓝按钮 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold !important;
        height: 3.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 5. 界面展示 ---
st.title("🔷 Máximojihe")
st.write("¡Qué onda! Sube una foto o escribe tu duda. Aquí no copiamos, aquí razonamos.")

uploaded_file = st.file_uploader("1. Sube tu ejercicio:", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_text = st.text_area("2. Escribe aquí el problema o tu duda:", placeholder="Ej: No entiendo este paso...")

# --- 6. 核心逻辑 (严格禁止答案) ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Pon una foto o escribe algo. 😉")
    else:
        with st.spinner("Máximojihe analizando..."):
            try:
                context_img = ""
                if uploaded_file:
                    base64_img = encode_image(uploaded_file)
                    ocr_res = client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Extract all text."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                    )
                    context_img = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("💡 Guía de Máximojihe")
                
                system_prompt = """
                Eres Máximojihe, tutor del Eton.
                REGLAS:
                1. NUNCA des el resultado numérico final.
                2. PROHIBIDO usar LaTeX (\boxed, \times).
                3. Explica los pasos con palabras: 'multiplica', 'divide'.
                4. Si te piden la respuesta, niégate amablemente.
                """

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Problema: {context_img} {user_text}. NO des el resultado."}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Máximojihe")
