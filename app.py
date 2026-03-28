import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. تظبيط شكل الصفحة
st.set_page_config(page_title="Prompt-X: استنساخ العوالم", page_icon="🪄", layout="centered")

st.title("🪄 Prompt-X: استنساخ العوالم!")
st.write("النسخة الأبدية المستقرة والمجانية 100% 🚀")

# 2. ربط مفتاح جوجل (العقل المدبر)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.warning("جاري تجهيز الموقع... تأكد من مفتاح جوجل.")

# 3. مكان رفع الصور
col1, col2 = st.columns(2)

with col1:
    scene_file = st.file_uploader("🖼️ ارفع المشهد المستهدف", type=["jpg", "jpeg", "png"])
    if scene_file:
        st.image(scene_file, caption="المشهد", use_container_width=True)

with col2:
    face_file = st.file_uploader("🧑 ارفع صورتك الشخصية", type=["jpg", "jpeg", "png"])
    if face_file:
        st.image(face_file, caption="الوجه", use_container_width=True)

# 4. زرار التشغيل
if st.button("🚀 تحليل الصور والحصول على البرومبت السري"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري تحليل ملامحك ورسم العالم الجديد (الموضوع سريع جداً)... ⏳"):
            try:
                # --- تحليل الوجه والمشهد باستخدام Gemini لتوليد البرومبت ---
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                
                # تحليل الوجه
                face_image = Image.open(face_file)
                face_prompt = "Analyze image_1.png and image_4.png: Identify the exact dark-rimmed rectangular frame of the glasses, the exact facial structure, and the genuinely wide cheerful smile. Focus on the geometry."
                face_desc = gemini_model.generate_content([face_prompt, face_image]).text.strip()
                
                # تحليل المشهد
                scene_image = Image.open(scene_file)
                scene_prompt = "Analyze image_2.png and image_5.png: Describe the deep canyon avenue lined with crumbling stone pillars, the central archway, and the distant mountains. Focus on the geometry."
                scene_desc = gemini_model.generate_content([scene_prompt, scene_image]).text.strip()
                
                # بناء البرومبت النهائي
                final_prompt = f"A breathtaking photorealistic cinematic masterpiece of a man, exact facial likeness, rectangular glasses, genuine wide cheerful smile, wearing grey polo shirt and dark pants, *sitting in a frontal pose* on the sand floor of [ {scene_desc} ]. 8k resolution, Unreal Engine 5 render, award winning photography, high quality"
                
                st.success("تم التحليل بنجاح! 🎉")
                
                st.subheader("البرومبت السري المستخدم:")
                st.code(final_prompt, language="text")
                
            except Exception as e:
                st.error(f"حصلت مشكلة: {e}")
