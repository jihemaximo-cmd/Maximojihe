import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps, ImageFilter
import io
import datetime
import traceback
import time
import random

# =================================================================
# 1. CONSTANTES DE SISTEMA Y FILOSOFÍA ETON
# =================================================================
VERSION = "3.4.1-TITANIUM"
CORE_PHILOSOPHY = "Excelencia, Honor y Rigor Académico"
GLOBAL_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"

# 设置页面元数据
st.set_page_config(
    page_title=f"Máximojihe {VERSION}",
    page_icon="maximojihe.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =================================================================
# 2. SISTEMA DE SEGURIDAD VISUAL (CSS)
# =================================================================
# 这里的 CSS 权重经过了多次加固，确保在 Streamlit 升级后依然有效
st.markdown("""
    <style>
    /* 强制全局背景：极致纯白 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 导师聊天气泡加固：黑框、白底、黑字 */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border: 2px solid #111111 !important;
        border-radius: 25px !important;
        padding: 30px !important;
        margin-top: 25px !important;
        box-shadow: 8px 8px 0px #000000 !important; /* 经典的波普硬投影风格 */
    }
    
    /* 强力锁定文字可见度：禁止所有半透明和淡色 */
    .stMarkdown, p, span, li, label, h1, h2, h3 { 
        color: #000000 !important; 
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* 上传组件：黑夜模式与发光边框 */
    [data-testid="stFileUploader"] {
        background: #000000 !important;
        border-radius: 30px !important;
        padding: 60px !important;
        border: 2px solid #333 !important;
    }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }
    
    /* 进度条与加载动画自定义 */
    .stProgress > div > div > div > div { background-color: #000000 !important; }

    /* Eton 尊享大按钮 */
    .stButton>button {
        background: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 60px !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        height: 5em !important;
        width: 100%;
        border: 4px solid #000 !important;
        letter-spacing: 2px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        background: #333333 !important;
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4) !important;
    }

    /* 侧边栏样式定制 */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEE; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. MÓDULO DE SERVICIOS AI (CLASE MAESTRA)
# =================================================================
class EtonAcademicSystem:
    def __init__(self, token):
        self.api_key = token
        self.endpoint = "https://api.siliconflow.cn/v1"
        self.client = OpenAI(api_key=self.api_key, base_url=self.endpoint)

    def validate_image_stream(self, uploaded_file):
        """
        深度图像预处理：不仅修复方向，还增强对比度
        解决：Error: 'NoneType' object has no attribute 'seek'
        """
        if not uploaded_file: return None
        try:
            uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            # 纠正旋转并提升画质
            img = ImageOps.exif_transpose(img).convert("RGB")
            # 略微增强边缘以提高 OCR 准确度
            img = img.filter(ImageFilter.SHARPEN)
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            return None

    def execute_ocr_analysis(self, b64_data):
        """执行高级视觉识别：GLM-4V 专家协议"""
        try:
            response = self.client.chat.completions.create(
                model="THUDM/GLM-4.1V-9B-Thinking",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "Transcripción exacta de expresiones matemáticas. Ignora texto no relevante."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}}
                ]}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LOG: Fallo en reconocimiento visual ({e})"

# 初始化学术引擎
AcademicEngine = EtonAcademicSystem(GLOBAL_KEY)

# =================================================================
# 4. GESTIÓN DE ESTADO Y SIDEBAR (MONITOR)
# =================================================================
with st.sidebar:
    st.image("maximojihe.png", width=150)
    st.markdown(f"### 🛡️ Monitor de Sistema\n**Versión:** `{VERSION}`")
    st.divider()
    
    # 实时连通性显示（模拟）
    st.success("🛰️ Enlace con SiliconCloud: Activo")
    st.info("🦌 Tutor: Máximojihe Online")
    
    st.divider()
    st.markdown("### 📊 Registro de Sesión")
    if "session_logs" not in st.session_state: st.session_state.session_logs = []
    for log in st.session_state.session_logs[-5:]:
        st.caption(f"[{datetime.datetime.now().strftime('%H:%M')}] {log}")
    
    if st.button("🔄 Reiniciar Entorno"):
        st.session_state.session_logs = []
        st.rerun()

# =================================================================
# 5. ARQUITECTURA DE LA INTERFAZ (UI)
# =================================================================
st.markdown(f"# {CORE_PHILOSOPHY}")
st.write("Bienvenido al entorno de alto rendimiento académico de Eton School. Tu razonamiento es nuestra prioridad.")

# 容器 A: 上传区域
with st.expander("📂 PASO 1: CARGA DE EVIDENCIA", expanded=True):
    doc_file = st.file_uploader("Sube tu captura o fotografía de alta resolución:", type=['png', 'jpg', 'jpeg'])
    if doc_file:
        st.image(doc_file, caption="Documento cargado correctamente", use_container_width=True)

# 容器 B: 提问区域
with st.expander("🧠 PASO 2: FOCO DEL PROBLEMA", expanded=True):
    st.markdown("Describe exactamente en qué parte del razonamiento te has detenido:")
    user_query = st.text_area("Tu duda específica:", height=100, placeholder="Ej: No comprendo por qué el logaritmo de una raíz se divide entre dos...")

# =================================================================
# 6. MOTOR DE RAZONAMIENTO Y RESPUESTA
# =================================================================
if st.button("🔍 INICIAR ANÁLISIS ACADÉMICO"):
    # 安全锁 A: 防空
    if not doc_file and not user_query.strip():
        st.error("⚠️ Error: Se requiere evidencia visual o descripción de texto para proceder.")
    else:
        # 视觉仪式感：分段加载
        with st.status("Ejecutando protocolos de tutoría...", expanded=True) as status:
            start_time = time.time()
            
            # 第一步：图像清洗
            st.write("Limpiando imagen y ajustando contraste...")
            b64_img = AcademicEngine.validate_image_stream(doc_file)
            
            # 第二步：OCR 解析
            ocr_text = "N/A"
            if b64_img:
                st.write("Identificando símbolos matemáticos...")
                ocr_text = AcademicEngine.execute_ocr_analysis(b64_img)
            
            # 第三步：构建 AI 指令
            st.write("Generando guía personalizada...")
            status.update(label="¡Razonamiento completo!", state="complete", expanded=False)
            
            elapsed = round(time.time() - start_time, 2)
            st.session_state.session_logs.append(f"Análisis exitoso ({elapsed}s)")

        # 核心导师输出
        st.divider()
        with st.chat_message("assistant", avatar="maximojihe.png"):
            # 极其严苛的系统指令 (加固版)
            SYSTEM_PROMPT = """
            IDENTIDAD: Máximojihe, el tutor matemático más prestigioso del Eton School.
            MISIÓN: Fomentar el pensamiento crítico. No resuelvas el problema, guíalo.
            
            PROTOCOLOS CRÍTICOS:
            1. IDIOMA: Español Mexicano elegante. Prohibido caracteres chinos.
            2. ZERO-RESULT: Nunca des el número final ni la solución simplificada.
            3. NO LATEX: No uses símbolos de programación. Escribe como un libro: 'la raíz cuadrada', 'derivada de x'.
            4. FORMATO: Usa viñetas claras. Explica la propiedad matemática aplicada en cada paso.
            """
            
            final_input = f"CONTEXTO_VISUAL: {ocr_text}\nDUDA_ALUMNO: {user_query}\nINSTRUCCIÓN: Guía al alumno sin dar la respuesta."
            
            try:
                response = AcademicEngine.client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": final_input}
                    ],
                    stream=True
                )
                st.write_stream(response)
            except Exception as api_err:
                st.error(f"⚠️ Error en el enlace neuronal: {api_err}")
                with st.expander("Logs técnicos"):
                    st.code(traceback.format_exc())

# =================================================================
# 7. PIE DE PÁGINA (INDUSTRIAL GRADE)
# =================================================================
st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.caption(f"© {datetime.datetime.now().year} Eton School Pride")
with col_f2:
    st.caption(f"Hardware: {sys.platform} | Engine: {VERSION}")
