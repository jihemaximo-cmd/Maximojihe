import streamlit as st
from openai import OpenAI
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA (带有硬编码图标) ---
# 这是一串经过 Base64 处理的图标数据，确保 100% 显示图标
icon_base64 = "iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAYAAABMhaUBAAAACXBIWXMAAAsTAAALEwEAmpwYAAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj33vRRxBy9Up" # (此处省略部分长字符串以保持代码简洁，实际代码中我会放完整)

st.set_page_config(
    page_title="Máximojihe", 
    page_icon="🦁", # 如果 Base64 太复杂，我们先用 Emoji 确保至少有一个帅气的狮子，或者按照下面的方法操作
    layout="centered"
)

# --- 2. 视觉 CSS (白底黑字 + 黑玻璃效果) ---
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
    [data-testid="stFileUploader"] svg { fill: #FFFFFF !important; }

    /* 输入框强制黑字 */
    .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        font-size: 16px !important;
        border: 1px solid #002D62 !important;
    }

    /* 按钮：Eton 蓝 */
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

# --- 3. API 初始化 ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面 ---
st.title("🦁 Máximojihe")
st.write("¡Qué onda! Saca una foto o escribe tu duda. No doy la respuesta, te doy la lógica.")

# 上传图片
uploaded_file = st.file_uploader("1. Sube tu ejercicio (Opcional):", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

# 纯文字对话
user_text = st.text_area("2. Escribe aquí el problema o tu duda:", placeholder="Ej: No entiendo este paso...")

# --- 5. 核心推理逻辑 ---
if st.button("🔍 ANALIZAR CON MÁXIMO"):
    if not uploaded_file and not user_text:
        st.warning("¡Oye! Pon una foto o escribe algo primero. 😉")
    else:
        with st.spinner("Máximojihe analizando..."):
            try:
                # 识别图片内容
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
                
                # 强力 Prompt 确保不泄题
                system_prompt = """
                Eres Máximojihe, tutor del Eton en CDMX.
                REGLAS:
                1. NUNCA des el resultado final.
                2. PROHIBIDO usar símbolos LaTeX o boxed.
                3. Guía paso a paso usando palabras normales.
                """

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Problema: {context_img} {user_text}. NO des la respuesta."}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Híjole, hubo un error: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Máximojihe")
