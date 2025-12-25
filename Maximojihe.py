import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageOps
import io
import time

# --- 1. CONFIGURACIÓN DE ÉLITE (PRO) ---
st.set_page_config(
    page_title="Máximojihe Tutor Pro v2.0", 
    page_icon="maximojihe.png", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS DE ALTO CONTRASTE (Nivel Eton) ---
st.markdown("""
    <style>
    /* 强制全局背景和文字对比 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 聊天气泡增强 */
    .stChatMessage {
        background-color: #F8F9FA !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02) !important;
    }
    
    /* 核心文字强制变黑，防止隐形 */
    .stChatMessage p, .stChatMessage li, .stChatMessage span, .stMarkdown { 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        font-size: 17px !important;
        line-height: 1.7 !important;
    }

    /* 优化上传组件外观 */
    [data-testid="stFileUploader"] {
        background-color: #121212 !important;
        border: 2px dashed #333 !important;
        border-radius: 25px !important;
        padding: 40px !important;
        transition: border 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover { border-color: #666 !important; }
    [data-testid="stFileUploader"] * { color: #FFFFFF !important; }

    /* 黑色 Eton 尊享按钮 */
    .stButton>button {
        background: linear-gradient(145deg, #1a1a1a, #000000) !important;
        color: #FFFFFF !important; 
        border: none !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        height: 4.2em !important;
        width: 100%;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
    }

    /* 状态提示颜色修复 */
    .stAlert { border-radius: 15px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SERVICIOS DE BACKEND (Resiliencia) ---
API_KEY = "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl"
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")

def optimize_image(uploaded_file):
    """自动修复图片旋转、缩放并编码，防止识别率低"""
    try:
        image = Image.open(uploaded_file)
        # 自动修复手机拍摄的旋转角度
        image = ImageOps.exif_transpose(image)
        # 转换为 RGB 防止部分 PNG 透明背景报错
        image = image.convert("RGB")
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=90)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        return None

# --- 4. GESTIÓN DE MEMORIA (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. INTERFAZ DE USUARIO ---
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.image("maximojihe.png", width=70)
with col_title:
    st.title("Máximojihe: Tutor de Élite")

with st.expander("📖 Reglas de Honor del Eton School"):
    st.write("- No pidas el resultado, pide el camino.")
    st.write("- El razonamiento es poder.")
    if st.button("Limpiar historial de chat"):
        st.session_state.messages = []
        st.rerun()

# 核心工作区
st.markdown("### 1. Preparación del ejercicio")
up_file = st.file_uploader("Arrastra tu imagen o toma una foto:", type=['png', 'jpg', 'jpeg'])

if up_file:
    # 预览图增强
    st.image(up_file, caption="Documento cargado correctamente", use_container_width=True)

st.markdown("### 2. Enfoque del problema")
u_text = st.text_area("¿Qué parte te genera dudas?", height=120, placeholder="Ej: No entiendo cómo aplicar la ley de los logaritmos en este paso...")

# --- 6. MOTOR DE RAZONAMIENTO MULTIMODAL ---
if st.button("🔍 INICIAR ANÁLISIS PASO A PASO"):
    # 极严密的空值验证
    if up_file is None and not u_text.strip():
        st.error("¡Oye! No puedo razonar en el vacío. Sube una foto o describe tu duda. 🦌")
    else:
        with st.spinner("Máximojihe está descifrando el conocimiento..."):
            try:
                # 步骤 A: 强化识图
                context_info = "El alumno no subió imagen."
                if up_file is not None:
                    # 使用优化后的图片函数
                    b64 = optimize_image(up_file)
                    if b64:
                        ocr_res = client.chat.completions.create(
                            model="THUDM/GLM-4.1V-9B-Thinking",
                            messages=[{"role": "user", "content": [
                                {"type": "text", "text": "Extract all math and text. If blurry, deduce by context. Be extremely detailed."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                            ]}]
                        )
                        context_info = ocr_res.choices[0].message.content

                # 步骤 B: 核心导师逻辑 (System Prompt 升级)
                with st.chat_message("assistant", avatar="maximojihe.png"):
                    sys_logic = """
                    IDENTIDAD: Eres Máximojihe, tutor del Eton School.
                    LENGUAJE: 100% Español (México). PROHIBIDO usar caracteres chinos.
                    MISIÓN: Guía socrática. No des el resultado final.
                    
                    REGLAS DE FORMATO:
                    1. NO USAR LATEX: No uses \, {, }, o frac. Escribe 'la raíz cuadrada de', 'todo eso sobre', etc.
                    2. VISIBILIDAD: Usa negritas para conceptos clave.
                    3. PASOS: Divide la explicación en 'Paso 1, Paso 2...'.
                    4. RESILIENCIA: Si el OCR es confuso, pídele al alumno que te confirme los datos.
                    """

                    # 构造增强 Prompt
                    full_prompt = f"INFO DE IMAGEN: {context_info}\nDUDA DEL ALUMNO: {u_text}\nINSTRUCCIÓN: Explica el razonamiento sin dar la respuesta."
                    
                    # 运行 DeepSeek 思考模型
                    response_stream = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        messages=[
                            {"role": "system", "content": sys_logic},
                            {"role": "user", "content": full_prompt}
                        ],
                        stream=True
                    )
                    
                    # 动态渲染输出
                    full_response = st.write_stream(response_stream)
                    # 存入记忆
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.exception(f"Error en el sistema de tutoría: {e}")

# 页脚
st.markdown("---")
st.markdown("<center style='color: #888;'>© 2025 Eton School Pride | Excelencia • Honor • Rigor</center>", unsafe_allow_html=True)
