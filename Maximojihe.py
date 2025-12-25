import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re
import os  # 已补全：解决刚才的 NameError

# =================================================================
# 1. 核心安全与环境配置 (STABLE CONFIG)
# =================================================================
# 建议后期将 Key 移至 Streamlit Cloud 的 Secrets 管理员后台
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

# 强制宽屏模式 + 标题
st.set_page_config(
    page_title="Máximojihe Elite", 
    page_icon="maximojihe.png", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================================
# 2. 视觉精确锁定：黑白极简风格 (PREMIUM UI)
# =================================================================
st.markdown("""
    <style>
    /* 全局背景锁定：纯白 */
    .stApp { background-color: #FFFFFF !important; }

    /* 全局字体：黑字，增加阅读质感 */
    .stMarkdown, h1, h2, h3, p, span, label {
        color: #000000 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* 隐藏所有 Streamlit 默认装饰 */
    #MainMenu, footer, header { visibility: hidden; }
    div[data-testid="stDecoration"] { display: none; }

    /* 有黑框区域：上传组件与输入框 */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 24px !important;
        padding: 30px !important;
        border: 1px solid #333 !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    .stTextArea textarea {
        color: #FFFFFF !important;
        background-color: #1A1C1E !important;
        border-radius: 16px !important;
        border: 1px solid #333 !important;
        font-size: 16px !important;
        padding: 15px !important;
    }

    /* 核心修复：黑色胶囊型按钮 */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 100px !important;
        padding: 15px 45px !important;
        border: none !important;
        width: auto !important;
        min-width: 280px !important;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease !important;
        display: block;
        margin: 0 auto;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(0,0,0,0.25) !important;
        background-color: #222222 !important;
    }
    
    /* 锁定按钮内文字颜色 */
    .stButton>button div, .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
    }

    /* AI 聊天气泡样式：优雅的灰白对比 */
    .stChatMessage {
        background-color: #FAFAFA !important;
        border: 1px solid #EAEAEA !important;
        border-radius: 20px !important;
        margin-bottom: 20px !important;
    }

    /* 加载动画颜色调整为黑色 */
    .stSpinner > div > div { border-top-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 后端处理引擎 (ENGINE LOGIC)
# =================================================================
class EliteEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def prepare_image(self, uploaded_file):
        """处理上传图片，支持旋转校正与 Base64 转换"""
        if uploaded_file is None: return None
        try:
            bytes_data = uploaded_file.getvalue()
            img = Image.open(io.BytesIO(bytes_data))
            img = ImageOps.exif_transpose(img).convert("RGB")
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            st.error(f"Error al procesar la imagen: {e}")
            return None

    def stream_filter(self, stream):
        """
        核心防剧透：
        1. 拦截并移除 <think> 标签内的所有内容
        2. 确保输出流干净稳定
        """
        is_thinking = False
        for chunk in stream:
            if not chunk.choices: continue
            delta = chunk.choices[0].delta.content
            if delta:
                if "<think>" in delta:
                    is_thinking = True
                    continue
                if "</think>" in delta:
                    is_thinking = False
                    continue
                if not is_thinking:
                    yield delta

# 初始化引擎
engine = EliteEngine(API_KEY)

# =================================================================
# 4. 界面布局 (STRUCTURE)
# =================================================================
# 顶部区域
header_col1, header_col2 = st.columns([0.15, 0.85])
with header_col1:
    # 刚才报错的逻辑已安全化
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=110)
    else:
        st.markdown("<div style='height:110px; display:flex; align-items:center;'><b>M.J.</b></div>", unsafe_allow_html=True)

with header_col2:
    st.markdown("<h1 style='margin-top:25px; letter-spacing: -1px;'>Máximojihe Elite</h1>", unsafe_allow_html=True)

st.markdown("<p style='color: #666 !important;'>Tu tutor privado de Eton College. Inteligente, preciso y sin spoilers.</p>", unsafe_allow_html=True)
st.markdown("---")

# 主体输入区
st.markdown("### 1. Sube tu desafío")
file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], help="Sube una foto clara de tu problema")

if file:
    st.image(file, use_container_width=True, caption="Imagen cargada correctamente")

st.markdown("### 2. ¿Qué te hace dudar?")
prompt_input = st.text_area("", placeholder="Ej: No entiendo el tercer paso de esta ecuación...", height=120)

# =================================================================
# 5. 核心推理执行 (EXECUTION)
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not file and not prompt_input.strip():
        st.warning("Por favor, introduce una duda o sube una imagen.")
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png" if os.path.exists("maximojihe.png") else None):
        try:
            # 第一步：识图引擎 (GLM-4V)
            with st.status("Máximojihe Neural Vision analizando...", expanded=False) as status:
                ocr_result = "No hay imagen."
                if file:
                    b64_image = engine.prepare_image(file)
                    if b64_image:
                        vision_call = engine.client.chat.completions.create(
                            model="THUDM/GLM-4.1V-9B-Thinking",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all text and math accurately."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                                ]
                            }]
                        )
                        ocr_result = vision_call.choices[0].message.content
                status.update(label="Visión completada", state="complete")

            # 第二步：深度导师逻辑 (DeepSeek-R1)
            # 强化 Prompt：严格禁止直接给答案，采用导师反问模式
            system_role = (
                "Eres Máximojihe, el tutor privado más prestigioso de Eton College. "
                "FILOSOFÍA: Nunca des la respuesta final. El alumno debe trabajar. "
                "\n\nINSTRUCCIONES:"
                "\n1. Analiza el contexto de la imagen y la duda."
                "\n2. Explica el concepto fundamental (la 'llave' del problema)."
                "\n3. Indica el primer paso lógico."
                "\n4. PROHIBIDO: Escribir el resultado final de cualquier operación."
                "\n5. Si te piden '¿Cuánto es 88x100?', responde explicando la regla de los ceros, pero haz que el alumno escriba el número final."
                "\n6. Usa español elegante y profesional. No uses LaTeX, solo texto simple."
            )
            
            # 开启流式响应
            chat_stream = engine.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": f"Contexto: {ocr_result}\nDuda: {prompt_input}"}
                ],
                stream=True
            )
            
            # 使用精英过滤器进行安全输出
            st.write_stream(engine.stream_filter(chat_stream))

        except Exception as err:
            st.error("Error técnico en el sistema de tutoría.")
            with st.expander("Logs para administración"):
                st.code(traceback.format_exc())

# 底层标记
st.markdown("<br><br><p style='text-align: center; color: #BBB; font-size: 10px; letter-spacing: 2px;'>MÁXIMOJIHE ELITE SYSTEM • NO DIRECT ANSWERS • SECURED BY DS-R1</p>", unsafe_allow_html=True)
