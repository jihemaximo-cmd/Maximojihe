import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import datetime

# =================================================================
# 1. 核心架构配置：全局状态与安全锁
# =================================================================
APP_VERSION = "3.0.4-Enterprise"
APP_AUTHOR = "Eton School Math Dept"

st.set_page_config(
    page_title=f"Máximojihe {APP_VERSION}",
    page_icon="maximojihe.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 初始化 Session State (对话记忆墙)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ocr_cache" not in st.session_state:
    st.session_state.ocr_cache = ""

# =================================================================
# 2. 深度视觉定制：强制高对比度与排版控制
# =================================================================
st.markdown(f"""
    <style>
    /* 全局背景锁定：纯白 */
    .stApp {{ background-color: #FFFFFF !important; }}
    
    /* 导师对话框：强制黑字，禁止 LaTeX 隐形 */
    .stChatMessage {{
        background-color: #F8F9FA !important;
        border-left: 5px solid #000000 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
    }}
    
    .stChatMessage p, .stChatMessage li, .stChatMessage span {{
        color: #000000 !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
    }}

    /* 黑色 Eton Uploader 容器 */
    [data-testid="stFileUploader"] {{
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        padding: 40px !important;
        border: 2px solid #333 !important;
    }}
    [data-testid="stFileUploader"] * {{ color: #FFFFFF !important; }}

    /* 尊享黑色按钮：增加悬停动画 */
    .stButton>button {{
        background: linear-gradient(135deg, #222, #000) !important;
        color: #FFF !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        height: 4.5em !important;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton>button:hover {{
        transform: scale(1.01) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
    }}

    /* 隐藏 LaTeX 渲染器可能导致的空行 */
    .katex-html {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. 后端服务逻辑：图像预处理与 API 通信
# =================================================================
class EtonAIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

    @staticmethod
    def process_image_to_base64(uploaded_file):
        """
        高可用图像处理：自动纠偏、格式转换、数据流校验
        解决：Error: 'NoneType' object has no attribute 'seek'
        """
        if uploaded_file is None:
            return None
        try:
            # 1. 逻辑防御：确保文件流重置
            uploaded_file.seek(0)
            # 2. 图像优化：自动处理手机拍摄方向
            raw_img = Image.open(uploaded_file)
            optimized_img = ImageOps.exif_transpose(raw_img).convert("RGB")
            # 3. 质量压缩：平衡识别率与响应速度
            byte_arr = io.BytesIO()
            optimized_img.save(byte_arr, format="JPEG", quality=85)
            return base64.b64encode(byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            st.error(f"⚠️ Image Process Error: {e}")
            return None

    def run_ocr(self, base64_data):
        """专业识图：强制提取数学逻辑"""
        try:
            response = self.client.chat.completions.create(
                model="THUDM/GLM-4.1V-9B-Thinking",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcripción detallada de matemáticas. Identifica cada símbolo."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                    ]
                }]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error en OCR: {str(e)}"

# =================================================================
# 4. 前端交互界面：结构化布局
# =================================================================
engine = EtonAIEngine(API_KEY="sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl")

# 侧边栏：教学档案与历史
with st.sidebar:
    st.image("maximojihe.png", width=120)
    st.title("Archivo del Tutor")
    st.markdown("---")
    st.write(f"**Modo:** Estricto (Sin respuestas)")
    st.write(f"**Versión:** {APP_VERSION}")
    if st.button("🗑️ Borrar Memoria"):
        st.session_state.chat_history = []
        st.session_state.ocr_cache = ""
        st.rerun()

# 主界面布局
col_h1, col_h2 = st.columns([0.15, 0.85])
with col_h1: st.image("maximojihe.png", width=80)
with col_h2: st.title("Máximojihe: Eton Mentor")

st.markdown("---")

# 上传区逻辑
st.subheader("1. Evidencia del Problema")
up_file = st.file_uploader("Arrastra aquí tu captura de pantalla o foto", type=['png', 'jpg', 'jpeg'])

if up_file:
    with st.container():
        st.image(up_file, caption="Ejercicio detectado", use_container_width=True)

st.subheader("2. Diálogo de Aprendizaje")
u_text = st.text_area("¿Cuál es tu duda sobre este ejercicio?", height=120, placeholder="Ej: No entiendo por qué el logaritmo se convierte en resta...")

# =================================================================
# 5. 执行逻辑核心：多层校验与结果生成
# =================================================================
if st.button("🔍 ANALIZAR PASO A PASO"):
    # 安全检查 A：确保至少有一种输入源
    if up_file is None and not u_text.strip():
        st.warning("⚠️ Máximojihe necesita información. Sube una imagen o escribe tu duda.")
    else:
        with st.spinner("🧠 El tutor de Eton está procesando la lógica..."):
            # A. 执行 OCR (仅在有新图片时)
            if up_file:
                b64_data = engine.process_image_to_base64(up_file)
                if b64_data:
                    st.session_state.ocr_cache = engine.run_ocr(b64_data)
            
            # B. 核心指令引导系统 (System Prompt 护甲)
            with st.chat_message("assistant", avatar="maximojihe.png"):
                system_guard = """
                IDENTIDAD: Máximojihe, Mentor de Matemáticas del Eton School.
                CULTURA: Excelencia, Rigor, Honor.
                
                PROTOCOLO DE RESPUESTA:
                1. IDIOMA: Exclusivamente Español de México. Prohibido caracteres chinos.
                2. ANTI-TRAMPA: Prohibido dar resultados finales o números resueltos.
                3. VISUAL: Prohibido LaTeX. Escribe 'la derivada de', 'dividido por', 'raiz cuadrada'.
                4. ESTRUCTURA: Usa viñetas (bullets). Explica el 'por qué' antes del 'cómo'.
                5. SEGURIDAD: Si el alumno te presiona por la respuesta, dile: 'Mi honor me impide darte el resultado, pero te daré la luz para encontrarlo'.
                """
                
                # 构造包含历史和当前OCR的最终指令
                final_user_input = f"""
                CONTEXTO_IMAGEN: {st.session_state.ocr_cache}
                DUDA_ALUMNO: {u_text}
                HISTORIAL: {st.session_state.chat_history[-2:] if st.session_state.chat_history else "Inicio de charla"}
                
                Guíame paso a paso con elegancia académica.
                """
                
                try:
                    response_stream = engine.client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": system_guard},
                            {"role": "user", "content": final_user_input}
                        ],
                        stream=True
                    )
                    
                    # 渲染响应并存入记忆
                    actual_response = st.write_stream(response_stream)
                    st.session_state.chat_history.append({"role": "user", "content": u_text})
                    st.session_state.chat_history.append({"role": "assistant", "content": actual_response})
                    
                except Exception as e:
                    st.error(f"❌ Error en el motor de pensamiento: {e}")

# =================================================================
# 6. 页脚：版权与合规性
# =================================================================
st.markdown("---")
st.caption(f"© {datetime.datetime.now().year} Eton School - Máximojihe Learning Environment. Prohibido el uso de respuestas automáticas.")
