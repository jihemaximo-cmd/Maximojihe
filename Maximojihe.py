import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import sys
import traceback

# =================================================================
# 1. 系统核心配置 (CORE ARCHITECTURE)
# =================================================================
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(
    page_title="Máximojihe: Tutor de Élite",
    page_icon="maximojihe.png",
    layout="wide" # 使用宽屏布局以匹配截屏的比例
)

# =================================================================
# 2. 视觉精确还原系统 (PIXEL PERFECT CSS)
# =================================================================
st.markdown("""
    <style>
    /* 强制全局白底黑字，解决所有不可见问题 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 锁定所有文字：漆黑、无透明度、清晰 */
    .stMarkdown, p, span, li, label, h1, h2, h3, div { 
        color: #000000 !important; 
        opacity: 1 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* 顶部 Logo 容器布局 */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }

    /* 上传区域：大圆角胶囊黑底 (完全匹配截屏1) */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 40px !important;
        padding: 30px !important;
        border: none !important;
        margin-top: 10px !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    /* 隐藏上传组件的多余边框 */
    [data-testid="stFileUploader"] section { border: none !important; }

    /* 输入区域：深色背景矩形 (完全匹配截屏) */
    .stTextArea textarea {
        background-color: #1A1C1E !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 15px !important;
    }

    /* 分析按钮：左对齐胶囊设计 + 放大镜符号 (完全匹配截屏3) */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 10px 30px !important;
        border: none !important;
        font-weight: bold !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        width: auto !important;
        min-width: 200px !important;
        height: 50px !important;
        font-size: 14px !important;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
        color: #FFFFFF !important;
    }

    /* 隐藏 Streamlit 官方杂质 */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 工业级后端引擎 (ENGINE BLOCK)
# =================================================================
class MaximojiheBackend:
    """
    后端处理类，包含图像流控制与 API 路由。
    修复了所有已知的 TypeError 和指针溢出问题。
    """
    def __init__(self, key):
        # 正确初始化 OpenAI 客户端，解决 133 行报错
        self.api_key = key
        self.client = OpenAI(api_key=self.api_key, base_url=BASE_URL)

    def process_image_to_base64(self, uploaded_file):
        """
        转换上传文件为 Base64。
        包含指针安全重置 (Seek 0)。
        """
        if uploaded_file is None:
            return None
        try:
            uploaded_file.seek(0)
            raw_img = Image.open(uploaded_file)
            # 自动修复 EXIF 旋转
            fixed_img = ImageOps.exif_transpose(raw_img).convert("RGB")
            
            # 转换为内存字节流
            buffer = io.BytesIO()
            fixed_img.save(buffer, format="JPEG", quality=95)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            st.error(f"Error en matriz de imagen: {e}")
            return None

# 启动核心
engine = MaximojiheBackend(API_KEY)

# =================================================================
# 4. 界面布局还原 (LAYOUT RECONSTRUCTION)
# =================================================================
# 顶部区域：Logo 与 标题
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.image("maximojihe.png", width=120)
with col_title:
    st.markdown("<h1 style='margin-top:20px;'>Máximojihe: Tutor de Élite</h1>", unsafe_allow_html=True)

st.markdown("<p style='font-size:14px; color:#555;'>Sube tu ejercicio. Mi misión es tu aprendizaje, no darte la respuesta. 🦌</p>", unsafe_allow_html=True)

# 核心功能区
st.write("")
st.markdown("**Sube tu imagen aquí:**")
doc_input = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="uploader_main")

if doc_input:
    st.image(doc_input, use_container_width=True)

st.write("")
st.markdown("**¿Qué te genera duda?**")
user_text = st.text_area("", placeholder="Describe lo que ves si la imagen no es clara...", height=120, key="query_main")

# =================================================================
# 5. 执行逻辑 (THE BRAIN)
# =================================================================
# 按钮文字包含放大镜 Emoji，模拟截屏中的图标
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not doc_input and not user_text.strip():
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 1. 视觉分析层
            context_data = ""
            if doc_input:
                b64_string = engine.process_image_to_base64(doc_input)
                if b64_string:
                    ocr_res = engine.client.chat.completions.create(
                        model="THUDM/GLM-4.1V-9B-Thinking",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract math structure."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_string}"}}
                            ]
                        }]
                    )
                    context_data = ocr_res.choices[0].message.content

            # 2. 逻辑引导层
            # 纯粹的专业导师指令，不带冗余标签
            sys_instr = (
                "Eres Máximojihe, un tutor experto. "
                "No des la respuesta final. Guía al alumno. "
                "Responde en español claro. "
                "No uses LaTeX. Escribe 'raiz de', 'cuadrado', etc."
            )
            
            full_user_input = f"Problema: {context_data}\nDuda: {user_text}"
            
            response = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_instr},
                    {"role": "user", "content": full_user_input}
                ],
                stream=True
            )
            st.write_stream(response)

        except Exception as critical_err:
            st.error("Error en el razonamiento del sistema.")
            with st.expander("Detalles"):
                st.code(traceback.format_exc())

# =================================================================
# 6. 页脚
# =================================================================
st.markdown("<br><p style='text-align: center; color: #BBB; font-size: 10px;'>MÁXIMOJIHE ACADEMIC ENGINE</p>", unsafe_allow_html=True)
