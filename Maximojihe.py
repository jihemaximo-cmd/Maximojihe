import streamlit as st
from openai import OpenAI
import base64

# --- 页面设置：符合 Eton 的高级感 ---
st.set_page_config(page_title="Eton Study Lab", page_icon="🎓")

# 注入 CSS 让界面更干净
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { border-radius: 10px; border: 1px solid #002d62; }
    </style>
    """, unsafe_allow_html=True)

# --- 初始化 API ---
API_KEY = st.secrets.get("sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl", "sk-rbafssagtaksrelgfqnzbhdjqtlhdmgthtlwskejckajcejl")
client = OpenAI(api_key=API_KEY, base_url="https://api.siliconflow.cn/v1")


def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')


st.title("🎓 Eton Digital Tutor")
st.write("¡Qué onda! 我是你的智能导学助手。拍张照片，我们一起把这题搞定！")

# 1. 拍照/上传功能
uploaded_file = st.file_uploader("拍下你的题目（拍清楚点，ojo ahí）", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='你的作业图片', use_container_width=True)

    if st.button("🔍 开始解析 (Analizar)"):
        with st.spinner("正在思考中... déjame checarlo..."):
            base64_img = encode_image(uploaded_file)

            try:
                # 第一步：GLM-4V 视觉识别 (免费版)
                # 这一步负责把图变成文字，它是我们的“眼睛”
                ocr_res = client.chat.completions.create(
                    model="THUDM/GLM-4.1V-9B-Thinking",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extrae el texto y fórmulas de esta imagen. No resuelvas."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                question_text = ocr_res.choices[0].message.content

                st.divider()
                st.subheader("💡 老师的思路引导 (Guía de Estudio)")

                # 第二步：DeepSeek-R1 逻辑推理 (最强免费推理模型)
                # 核心：用西语精英口音拒绝给答案
                system_prompt = """
                你是一位在墨西哥 Eton School 工作的顶级私教。
                你的说话风格是 'Fresa' (CDMX 精英口音)：非常有礼貌、自信、现代。

                【关键指令】
                1. 绝对不准给出最终答案！
                2. 说话要带墨西哥本地精英口音。常用词：'Ojo aquí', 'Fíjate bien', 'No manches, está súper fácil', 'Te explico la lógica'.
                3. 如果学生求你给答案，你要幽默且坚定地拒绝。

                【引导步骤】
                - Concepto: 先解释这题在考什么知识点。
                - El truco: 提示解题的关键陷阱在哪。
                - El empujoncito: 给出解题的第一步公式或逻辑，剩下的让他们自己算。
                """

                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"题目内容：{question_text}\n请用西语引导我，但别给我答案。"}
                    ],
                    stream=True
                )

                # 在页面上流式展示 AI 的思考和西语引导
                st.write_stream(response)

            except Exception as e:
                st.error(f"哎呀，出错了 (Híjole, algo salió mal): {e}")

st.markdown("---")
st.caption("🇲🇽 为 Eton 社区定制 | 遵守学校学术诚信准则")