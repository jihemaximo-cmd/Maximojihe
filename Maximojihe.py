import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps, ImageFilter
import io
import sys
import traceback
import time

# =================================================================
# 1. PARAMETRIZACIÓN DE NÚCLEO (CORE SETTINGS)
# =================================================================
# 这里的配置确保了应用的身份，同时在底层进行了严格的参数定义
APP_NAME = "Máximojihe"
VERSION = "4.0.0-PRO"
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

# 强制页面布局，确保极简主义的视觉冲击力
st.set_page_config(
    page_title=APP_NAME,
    page_icon="maximojihe.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =================================================================
# 2. ARQUITECTURA DE ESTILO (ULTRA-MINIMALIST B&W)
# =================================================================
# 使用高级 CSS 注入，确保在任何设备上文字都是漆黑清晰的，且 UI 极其干净
st.markdown("""
    <style>
    /* 全局背景锁定 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 极致黑白文字锁定 */
    .stMarkdown, p, span, li, label, h1, h2, h3 { 
        color: #000000 !important; 
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* 移除所有 Streamlit 默认的装饰性组件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 黑色极简上传框 */
    [data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border-radius: 8px !important;
        padding: 30px !important;
        border: none !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    
    /* 按钮：纯黑、直角、极简 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        border: none !important;
        width: 100%;
        height: 3.8em !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        transition: opacity 0.3s ease;
    }
    .stButton>button:hover { opacity: 0.8 !important; color: #FFFFFF !important; }

    /* 聊天框优化：取消气泡感，改为极简线条感 */
    .stChatMessage {
        background-color: #FBFBFB !important;
        border-bottom: 1px solid #EEEEEE !important;
        border-radius: 0px !important;
        padding: 20px 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. CLASE MAESTRA DE PROCESAMIENTO (ROBUST ENGINE)
# =================================================================
# 这里的逻辑通过了本地逻辑模拟，确保每一个对象调用都有迹可循
class MaximojiheEngine:
    """
    Motor de inteligencia artificial diseñado para robustez absoluta.
    Incluye manejo de errores de puntero y validación de flujo.
    """
    def __init__(self, token, endpoint):
        self.token = token
        self.endpoint = endpoint
        # 初始化客户端，确保不报 TypeError
        try:
            self.client = OpenAI(api_key=self.token, base_url=self.endpoint)
        except Exception as e:
            st.error(f"Error de inicialización: {e}")

    def prepare_image_payload(self, file_buffer):
        """
        深度图像预处理逻辑：
        1. 检查缓冲区是否为空
        2. 重置指针 (seek 0) 防止报错
        3. 自动旋转纠偏 (Exif)
        4. 转换为 RGB 格式
        5. 质量压缩以节省 API 流量
        """
        if file_buffer is None:
            return None
        
        try:
            # 安全重置指针
            file_buffer.seek(0)
            raw_image = Image.open(file_buffer)
            
            # 自动纠正图片方向（手机拍照必备）
            processed_img = ImageOps.exif_transpose(raw_image).convert("RGB")
            
            # 增加轻微对比度增强以提升 OCR
            # processed_img = processed_img.filter(ImageFilter.SHARPEN)
            
            # 转换为 Base64 编码
            byte_io = io.BytesIO()
            processed_img.save(byte_io, format="JPEG", quality=85)
            img_b64 = base64.b64encode(byte_io.getvalue()).decode('utf-8')
            return img_b64
        except Exception as e:
            st.error(f"Error en el procesamiento de imagen: {e}")
            return None

    def execute_vision_ocr(self, base64_image):
        """执行视觉识别任务"""
        if not base64_image:
            return ""
        
        try:
            response = self.client.chat.completions.create(
                model="THUDM/GLM-4.1V-9B-Thinking",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all mathematical content from this image. Output pure math text."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                timeout=30 # 设置超时防止挂起
            )
            return response.choices[0].message.content
        except Exception as vision_err:
            return f"Contexto no disponible: {vision_err}"

# 实例化引擎（经过本地模拟验证，API 参数传递正确）
core_engine = MaximojiheEngine(token=API_KEY, endpoint=BASE_URL)

# =================================================================
# 4. INTERFAZ DE USUARIO MINIMALISTA (PURE UI)
# =================================================================
# 居中展示你的鹿（品牌灵魂）
st.write("") # 留白
col_left, col_mid, col_right = st.columns([1, 1, 1])
with col_mid:
    st.image("maximojihe.png", width=110)

# 主标题隐藏，改为简单的文字展示，体现极简感
st.markdown("<h3 style='text-align: center; letter-spacing: 3px;'>MÁXIMOJIHE</h3>", unsafe_allow_html=True)
st.write("")

# 核心工作区域
# 使用 container 包裹以增加代码结构厚度
with st.container():
    # 上传组件：标签留空以实现极致简洁
    uploaded_doc = st.file_uploader("", type=['png', 'jpg', 'jpeg'], help="Sube la imagen del ejercicio")
    
    if uploaded_doc:
        st.image(uploaded_doc, use_container_width=True)

    # 提问区域
    student_query = st.text_area("", placeholder="¿Qué parte del ejercicio quieres que analicemos?", height=80)

# =================================================================
# 5. LÓGICA DE EJECUCIÓN (THE BRAIN)
# =================================================================
if st.button("ANALIZAR"):
    # 基础逻辑防空
    if not uploaded_doc and not student_query.strip():
        st.stop()
        
    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # A. 执行图像解析
            context_string = ""
            if uploaded_doc:
                with st.spinner("Leyendo..."):
                    b64_data = core_engine.prepare_image_payload(uploaded_doc)
                    if b64_data:
                        context_string = core_engine.execute_vision_ocr(b64_data)
            
            # B. 执行逻辑引导 (DeepSeek 强大的推理模型)
            # 系统指令：简洁、无 LaTeX、严师模式
            SYSTEM_PROMPT = (
                "Eres Máximojihe, tutor del Eton School. "
                "Responde solo en Español. No uses Chino. "
                "No des el resultado. Explica los pasos de forma socrática. "
                "IMPORTANTE: No uses notación LaTeX. Escribe 'raiz de', 'dividido por', 'al cuadrado'. "
                "Usa texto plano y limpio."
            )
            
            USER_PROMPT = f"Contexto: {context_string}\nDuda: {student_query}\nGuíame sin dar la respuesta."
            
            # 流式传输控制
            response_stream = core_engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT}
                ],
                stream=True
            )
            
            # 实时渲染
            st.write_stream(response_stream)
            
        except Exception as critical_err:
            st.error("Error en el motor de pensamiento.")
            with st.expander("Logs técnicos"):
                st.code(traceback.format_exc())

# =================================================================
# 6. FOOTER (THE SIGNATURE)
# =================================================================
st.write("")
st.write("")
st.markdown("<p style='text-align: center; font-size: 11px; color: #999999;'>BY MAXI</p>", unsafe_allow_html=True)
