import streamlit as st
import google.generativeai as genai
from PIL import Image
from gradio_client import Client, handle_file
import tempfile
import os
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Prompt-X: المستكشف", page_icon="🪄", layout="centered")

st.title("🪄 Prompt-X: استنساخ العوالم")
st.write("نسخة الإصلاح النهائي: حل مشكلة السواد وتثبيت المطابقة 🚀")

# 2. ربط جوجل
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("تأكد من وجود GOOGLE_API_KEY في الـ Secrets")

# 3. رفع الصور
col1, col2 = st.columns(2)
with col1:
    scene_file = st.file_uploader("🖼️ صورة المشهد", type=["jpg", "png", "jpeg"])
with col2:
    face_file = st.file_uploader("🧑 صورتك الشخصية", type=["jpg", "png", "jpeg"])

if st.button("🚀 ابدأ التحويل"):
    if scene_file and face_file:
        with st.spinner("جاري المعالجة الذكية... (قد تستغرق دقيقة) ⏳"):
            try:
                # أ- تجهيز الصور
                face_img = Image.open(face_file).convert("RGB")
                scene_img = Image.open(scene_file).convert("RGB")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f_tmp:
                    face_img.save(f_tmp.name, quality=95)
                    f_path = f_tmp.name
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as s_tmp:
                    scene_img.save(s_tmp.name, quality=95)
                    s_path = s_tmp.name

                # ب- تحليل Gemini (برومبت مبسط جداً لعدم استفزاز الفلاتر)
                model = genai.GenerativeModel('gemini-2.0-flash')
                analysis = model.generate_content(["Describe the lighting and colors of this place in 5 words:", scene_img])
                style_desc = analysis.text.strip()

                # ج- الاتصال بالسيرفر (استخدام نسخة مغايرة)
                client = Client("Zhen-An/InstantID") # سيرفر بديل
                
                # إرسال البيانات (Positional Arguments)
                result = client.predict(
                    handle_file(f_path), # Face
                    handle_file(s_path), # Pose/Scene
                    f"A high-quality cinematic portrait of a man, {style_desc}, photorealistic, masterwork", # Prompt
                    "black image, dark, blurry, nsfw, distorted, ugly, bad anatomy", # Negative Prompt (إضافة منع السواد)
                    "(No style)", # Style
                    20,    # Steps (تقليل الخطوات يقلل احتمالية السواد)
                    0.4,   # Identity Strength (تقليل القوة لتفادي الـ Crash)
                    0.4,   # Image Adapter Strength
                    5.0,   # Guidance
                    random.randint(1, 999999), # Seed
                    api_name="/generate_image"
                )

                # د- التظهير النهائي
                st.success("تم التوليد!")
                res_path = result[0] if isinstance(result, (list, tuple)) else result
                final_output = Image.open(res_path).convert("RGB")
                
                st.image(final_output, caption="النتيجة النهائية", use_container_width=True)
                
                # زر التحميل
                with open(res_path, "rb") as img_file:
                    st.download_button("📥 تحميل الصورة", img_file, "result.jpg", "image/jpeg")

                # تنظيف
                os.remove(f_path)
                os.remove(s_path)

            except Exception as e:
                st.error(f"عذراً، السيرفر يواجه ضغطاً كبيراً. حاول مرة أخرى. (Error: {e})")
    else:
        st.warning("يرجى رفع الصورتين أولاً.")
