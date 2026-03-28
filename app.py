import streamlit as st
import google.generativeai as genai
from PIL import Image
from gradio_client import Client, handle_file
import tempfile
import os

st.set_page_config(page_title="Prompt-X: انقل وجهك!", page_icon="🧑‍🎤", layout="centered")

st.title("🧑‍🎤 Prompt-X: انقل وجهك لأي عالم!")
st.write("النسخة المفتوحة المصدر - مجانية 100% للأبد باستخدام مجتمع Hugging Face 🚀")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.warning("جاري تجهيز الموقع... تأكد من إعدادات المفاتيح السرية.")

col1, col2 = st.columns(2)

with col1:
    scene_file = st.file_uploader("🖼️ ارفع المشهد المستهدف", type=["jpg", "jpeg", "png"])
    if scene_file:
        st.image(scene_file, caption="المشهد", use_container_width=True)

with col2:
    face_file = st.file_uploader("🧑 ارفع صورتك الشخصية", type=["jpg", "jpeg", "png"])
    if face_file:
        st.image(face_file, caption="الوجه", use_container_width=True)

if st.button("🚀 انقلني لهذا العالم!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري تحليل المشهد ودمج العوالم (برجاء الانتظار دقيقة أو دقيقتين، نحن نستخدم سيرفرات مجانية)... ⏳"):
            try:
                scene_image = Image.open(scene_file)
                gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                scene_analysis_prompt = """
                أنت خبير تصوير. حلل هذه الصورة بدقة لإضاءتها وألوانها والبيئة.
                اكتب Prompt باللغة الإنجليزية يصف هذه البيئة. لا تصف الأشخاص، صف فقط المشهد والملابس.
                اكتب البرومبت كسطر واحد فقط.
                """
                gemini_response = gemini_model.generate_content([scene_analysis_prompt, scene_image])
                base_prompt = gemini_response.text.strip()
                
                face_image = Image.open(face_file)
                face_image.thumbnail((800, 800))
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    face_image.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                final_prompt = f"A photorealistic portrait of a man img, {base_prompt}, cinematic lighting, 8k resolution, highly detailed"
                
                client = Client("TencentARC/PhotoMaker")
                
                client = Client("TencentARC/PhotoMaker")
                
                result = client.predict(
                    handle_file(tmp_path), 
                    final_prompt,
                    "nsfw, generic face, badly drawn, distorted, low quality",
                    "(No style)",
                    20,
                    20,
                    1,
                    5,
                    0,
                    api_name="/generate_image"
                )
                
                st.success("تم التوليد بنجاح من السيرفر المجاني! 🎉")
                st.balloons()
                st.subheader("إنت دلوقتي في العالم الجديد:")
                
                if isinstance(result, tuple) or isinstance(result, list):
                    st.image(result[0], use_container_width=True)
                else:
                    st.image(result, use_container_width=True)
                    
                os.remove(tmp_path)
                    
            except Exception as e:
                st.error(f"حصل خطأ أو السيرفر المجاني عليه ضغط حالياً. التفاصيل: {e}")
