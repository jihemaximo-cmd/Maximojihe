import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import traceback
import re

# =================================================================
# 1. 核心安全配置 (ZERO-BUG CONFIG)
# =================================================================
# 建议：以后可以将 Key 放在 st.secrets 中以防泄露
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
BASE_URL = "https://api.siliconflow.cn/v1"

st.set_page_config(page_title="Máximojihe Elite", page_icon="maximojihe.png", layout="wide")

# =================================================================
# 2. 视觉精确锁定：黑白极简风格 (Elite UI)
# =================================================================
st.markdown("""
    <style>
    /* 全局背景：纯白 */
    .stApp { background-color: #FFFFFF !important; }

    /* 无黑框区域强制黑字 */
    .stMarkdown, h1, h2, h3, p, span, div[data-testid="stExpander"] p {
        color: #000000 !important;
        opacity: 1 !important;
    }

    /* 有黑框区域（上传和输入）强制白字 */
    [data-testid="stFileUploader"] * {
        color: #FFFFFF !important;
    }
    
    .stTextArea textarea {
        color: #FFFFFF !important;
        background-color: #1A1C1E !important;
        border-radius: 12px !important;
        border: none !important;
        font-size: 16px !important;
    }

    /* 区域样式设定 */
    [data-testid="stFileUploader"] {
        background-color: #1A1C1E !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }

    /* 按钮：胶囊形状，黑色背景，白色文字 */
    .stButton>button {
        background-color: #000000 !important;
        border-radius: 100px !important;
        padding: 10px 35px !important;
        border: none !important;
        width: auto !important;
        min-width: 250px !important;
        height: 60px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
    }
    
    /* 暴力锁定按钮文字 */
    .stButton>button div, .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
        letter-spacing: 1px !important;
    }

    /* AI 回复区样式 */
    .stChatMessage {
        background-color: #F8F9FA !important;
        border: 1px solid #EEE !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    /* 隐藏所有多余的 Streamlit 组件 */
    #MainMenu, footer, header { visibility: hidden; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 后端加固引擎与过滤器 (ELITE FILTER ENGINE)
# =================================================================
class MaxiEngine:
    def __init__(self, key):
        self.client = OpenAI(api_key=key, base_url=BASE_URL)

    def process_image(self, file):
        if file is None: return None
        try:
            file.seek(0)
            img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception:
            return None

    def elite_stream_filter(self, stream):
        """
        核心防剧透逻辑：彻底切断 <think> 标签，并实时监控输出内容
        """
        is_thinking = False
        for chunk in stream:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                # 拦截思维链开始
                if "<think>" in content:
                    is_thinking = True
                    continue
                # 拦截思维链结束
                if "</think>" in content:
                    is_thinking = False
                    continue
                
                # 只有当模型不在自言自语时，才把文字吐给用户
                if not is_thinking:
                    yield content

# 初始化
handler = MaxiEngine(API_KEY)

# =================================================================
# 4. 界面布局 (UI DESIGN)
# =================================================================
# 顶部品牌展示
t_col1, t_col2 = st.columns([0.15, 0.85])
with t_col1:
    if os.path.exists("maximojihe.png"):
        st.image("maximojihe.png", width=110)
    else:
        st.markdown("### [LOGO]")
with t_col2:
    st.markdown("<h1 style='margin-top:20px; letter-spacing: 2px;'>MÁXIMOJIHE</h1>", unsafe_allow_html=True)

# 功能操作区
st.markdown("**Sube tu ejercicio aquí (Matemáticas, Física, Química):**")
up_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
if up_file:
    st.image(up_file, use_container_width=True, caption="Imagen cargada correctamente")

st.markdown("**¿Qué parte no entiendes?**")
user_text = st.text_area("", placeholder="Ejemplo: No entiendo cómo despejar la X...", height=120)

# =================================================================
# 5. 核心逻辑执行 (THE BRAIN)
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
    if not up_file and not user_text.strip():
        st.warning("Por favor, sube una imagen o escribe tu duda.")
        st.stop()

    with st.chat_message("assistant", avatar="maximojihe.png"):
        try:
            # 第一阶段：视觉解析 (GLM-4V)
            ocr_content = "No image provided."
            if up_file:
                with st.spinner("Interpretando imagen..."):
                    b64_img = handler.process_image(up_file)
                    if b64_img:
                        vision_res = handler.client.chat.completions.create(
                            model="THUDM/GLM-4.1V-9B-Thinking",
                            messages=[{
                                "role": "user", 
                                "content": [
                                    {"type": "text", "text": "Extract all data and equations from this image precisely."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                                ]
                            }]
                        )
                        ocr_content = vision_res.choices[0].message.content

            # 第二阶段：逻辑引导 (DeepSeek-R1 + Elite Prompt)
            # 这里的 Prompt 经过极限调优，专门防止剧透
            sys_prompt = (
                "Eres Máximojihe, el tutor de élite de Eton College. "
                "TU MISIÓN: Guiar al alumno mediante el método socrático. "
                "\nREGLAS INNEGOCIABLES:"
                "\n1. PROHIBIDO dar la respuesta final o el resultado numérico de los cálculos."
                "\n2. Si el alumno pregunta '¿Cuánto es 88x100?', NO respondas '8800'. Explica que hay que añadir dos ceros y pregunta: '¿Qué número obtienes al hacerlo?'."
                "\n3. Responde siempre en español académico y motivador."
                "\n4. No uses LaTeX. Usa texto plano o símbolos simples (x, /, +, =)."
                "\n5. Estructura: A) Pista conceptual. B) Primer paso lógico. C) Pregunta abierta para el alumno."
                "\n6. Detente antes de llegar al último paso del cálculo."
            )
            
            # 发起流式请求
            response_stream = handler.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Datos del problema: {ocr_content}\nDuda del alumno: {user_text}"}
                ],
                stream=True
            )
            
            # 使用我们开发的精英过滤器进行输出
            st.write_stream(handler.elite_stream_filter(response_stream))

        except Exception as e:
            st.error("Error crítico en el motor neuronal.")
            with st.expander("Admin Debug Detail"):
                st.code(traceback.format_exc())

# 页脚
st.markdown("<br><hr><p style='text-align: center; color: #BBB; font-size: 11px; letter-spacing: 3px;'>MÁXIMOJIHE • ELITE ACADEMIC SYSTEM • V6.0</p>", unsafe_allow_html=True)
