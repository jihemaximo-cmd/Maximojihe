import streamlit as st
from openai import OpenAI
import base64

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="Máximo: Eton Study Lab", page_icon="🦁")

# --- 2. 核心视觉：白底黑字 + 黑玻璃上传框 ---
st.markdown("""
    <style>
    /* 整个页面强制白底黑字 */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    h1, h2, h3, p, span, label, div {
        color: #1E1E1E !important;
    }

    /* 关键：黑玻璃效果上传框 */
    [data-testid="stFileUploader"] {
        background: rgba(30, 30, 30, 0.9) !important; /* 深黑色半透明背景 */
        backdrop-filter: blur(10px) !important;       /* 毛玻璃模糊效果 */
        border-radius: 15px !important;
        padding: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    /* 强制上传框内的文字变白（为了在黑玻璃上能看清） */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }
    
    /* 上传框的小图标也变白 */
    [data-testid="stFileUploader"] svg {
        fill: #FFFFFF !important;
    }

    /* 按钮：Eton 蓝底白字 */
    .stButton>button {
        background-color: #002D62 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        border: none !important;
        height: 3.5em !important;
        font-weight: bold !important;
        margin-top: 10px !important;
    }

    /* 修正底部分割线 */
    hr { border-top: 1px solid #EEEEEE !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 API ---
# 使用你之前在截图里展示的那个 Key
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 4. 界面内容 (全西语) ---
st.title("🦁 Máximo AI")
st.write("¡Qué onda! Soy **Máximo**. Saca una foto de tu ejercicio y armamos la estrategia.")

# 这个框现在是黑玻璃效果了
uploaded_file = st.file_uploader("Sube tu ejercicio aquí (ojo ahí, que se vea claro):", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # 为了美观，预览图下方加一点间距
    st.image(uploaded_file, caption='Tu ejercicio cargado', use_container_width=True)

    if st.button("🔍 ANALIZAR CON MÁXIMO"):
        with st.spinner("Máximo está analizando..."):
            base64_img = encode_image(uploaded_file)
            try:
                # 眼睛：GLM-4V 识图
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extrae el texto de esta imagen. No resuelvas."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                question_text = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("📝 Estrategia de Máximo")

                # 大脑：DeepSeek-R1 引导
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": "Eres Máximo, un tutor fresa de Eton México. Habla con estilo, no des respuestas finales, solo guía los pasos lógicos."},
                        {"role": "user", "content": f"Texto del ejercicio: {question_text}\nAyúdame a entender los conceptos clave."}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as e:
                st.error(f"Híjole, algo salió mal: {e}")

st.markdown("---")
st.caption("🇲🇽 Eton School | Honor Code: Honestidad Académica")
