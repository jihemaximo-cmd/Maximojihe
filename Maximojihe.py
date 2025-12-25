import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback

# =================================================================
# 1. 基础配置：极简、稳重
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(
    page_title="Máximojihe",
    page_icon="maximojihe.png",
    layout="centered"
)

# =================================================================
# 2. 视觉加固：解决“看不见”的问题
# =================================================================
st.markdown("""
    <style>
    /* 核心：强制背景白，文字黑 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 锁定所有可能的文本元素为黑色，不透明度100% */
    .stMarkdown, p, span, li, label, h1, h2, h3, div { 
        color: #000000 !important; 
        opacity: 1 !important;
    }
    
    /* 聊天框：浅灰色背景，黑色文字 */
    .stChatMessage {
        background-color: #F0F2F6 !important;
        border-radius: 10px !important;
        color: #000000 !important;
    }
    
    /* 隐藏所有多余的 Streamlit 官方组件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 上传按钮：黑色长方块，符合你发的图片风格 */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 50px !important; /* 圆角矩形 */
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 分析按钮：黑色加粗 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        width: 100%;
        height: 3.5em !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 核心引擎：逻辑防崩
# =================================================================
class AIHandler:
    def __init__(self, key):
        # 实例化时直接传入 key，避免参数名错误
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file_data):
        """处理图像，确保 seek 指针不报错"""
        if file_data is None:
            return None
        try:
            file_data.seek(0)
            img = Image.open(file_data)
            # 自动修复拍照旋转问题
            img = ImageOps.exif_transpose(img).convert("RGB")
            
            byte_io = io.BytesIO()
            img.save(byte_io, format="JPEG")
            return base64.b64encode(byte_io.getvalue()).decode('utf-8')
        except Exception as e:
            st.error(f"Error al procesar imagen: {e}")
            return None

# 初始化引擎
handler = AIHandler(API_KEY)

# =================================================================
# 4. 界面排版：只保留你的鹿和功能
# =================================================================
# 顶部图标
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("maximojihe.png", width=120)

st.markdown("<h2 style='text-align: center;'>Máximojihe</h2>", unsafe_allow_html=True)

# 功能区
uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

user_input = st.text_area("¿Cuál es tu duda?", placeholder="Escribe aquí el problema o pregunta...")

# =================================================================
# 5. 执行逻辑：简洁、稳定、无 LaTeX
# =================================================================
if st.button("ANALIZAR"):
    if not uploaded_file and not user_input.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 第一阶段：识图
            ocr_text = ""
            if uploaded_file:
                b64_img = handler.process_image(uploaded_file)
                if b64_img:
                    ocr_res = handler.client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract math content."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }]
                    )
                    ocr_text = ocr_res.choices[0].message.content

            # 第二阶段：逻辑推理 (DeepSeek)
            # 这里的指令彻底去掉了“天才/CTO”的废话，就是正常的专业导师
            system_prompt = (
                "Eres Máximojihe, un tutor académico. "
                "Responde en español claro. "
                "Guía al estudiante paso a paso. "
                "No des el resultado final. "
                "No uses LaTeX. Escribe con palabras normales (ej. 'raiz cuadrada', 'dividido por')."
            )
            
            response = handler.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Problema: {ocr_text}\nPregunta: {user_input}"}
                ],
                stream=True
            )
            st.write_stream(response)

        except Exception as err:
            st.error("Error en el análisis.")
            with st.expander("Debug Info"):
                st.code(traceback.format_exc())

# =================================================================
# 6. 页脚
# =================================================================
st.markdown("<br><p style='text-align: center; color: #888;'>Máximojihe Academic System</p>", unsafe_allow_html=True)
