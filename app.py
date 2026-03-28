import streamlit as st
import google.generativeai as genai
from PIL import Image
from gradio_client import Client, handle_file
import tempfile
import os
import random

# 1. تظبيط شكل الصفحة
st.set_page_config(page_title="Prompt-X: استنساخ العوالم", page_icon="🪄", layout="centered")

st.title("🪄 Prompt-X: استنساخ العوالم!")
st.write("النسخة المتكاملة: دمج دقيق لملامحك ووضعيتك داخل الموقع بدون الخروج منه 🚀")

# 2. ربط مفتاح جوجل
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
if st.button("🚀 اخلق هذا العالم الآن!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري دمج ملامحك مع البيئة (برجاء الانتظار، قد تستغرق دقيقة أو دقيقتين لضمان دقة 100%)... ⏳"):
            try:
                # --- الخطوة أ: حفظ الصور مؤقتاً لإرسالها للسيرفر ---
                face_image = Image.open(face_file)
                scene_image = Image.open(scene_file)
                
                # تصغير بسيط لتسريع الرفع
                face_image.thumbnail((800, 800))
                scene_image.thumbnail((800, 800))
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_face:
                    face_image.save(tmp_face.name)
                    face_path = tmp_face.name
                    
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_scene:
                    scene_image.save(tmp_scene.name)
                    scene_path = tmp_scene.name

                # --- الخطوة ب: تحليل المشهد لاستخراج برومبت البيئة (جوجل) ---
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                scene_prompt_text = "Analyze this environment accurately in one short English sentence. Focus on the lighting, background, and atmosphere. Do not describe the person."
                scene_desc = gemini_model.generate_content([scene_prompt_text, scene_image]).text.strip()
                
                final_prompt = f"A photorealistic masterpiece of a man, {scene_desc}, 8k resolution, highly detailed, award winning photography"

                # --- الخطوة ج: الاتصال السري بسيرفر InstantID للمطابقة (بدون خروج العميل) ---
                # السيرفر ده بياخد الوش (للهوية) والمشهد (للوضعية والبيئة)
                client = Client("instantX/InstantID")
                
                # --- الخطوة ج: الاتصال السري بسيرفر InstantID للمطابقة ---
                client = Client("instantX/InstantID")
                
                # إرسال البيانات بالترتيب المباشر لتفادي أي تغيير في أسماء المتغيرات على السيرفر
                result = client.predict(
                    handle_file(face_path),                                              # 1. صورة الوجه
                    handle_file(scene_path),                                             # 2. صورة الوضعية (المشهد)
                    final_prompt,                                                        # 3. البرومبت
                    "nsfw, generic face, badly drawn, distorted, low quality, cartoon",  # 4. البرومبت السلبي
                    "(No style)",                                                        # 5. الستايل
                    20,                                                                  # 6. عدد الخطوات
                    0.8,                                                                 # 7. قوة مطابقة الوجه
                    0.8,                                                                 # 8. قوة مطابقة البيئة
                    5,                                                                   # 9. قوة التوجيه
                    random.randint(1, 100000),                                           # 10. Seed
                    api_name="/generate_image"
                )

                # --- الخطوة د: تظهير الصورة (حل مشكلة الصورة السوداء) ---
                st.success("تم تخليق العالم والمطابقة بنجاح! 🎉")
                st.balloons()
                
                st.subheader("إنت دلوقتي في العالم الجديد:")
                
                # تحويل النتيجة لصورة صالحة للعرض
                final_img_path = result[0] if isinstance(result, (tuple, list)) else result
                image_bytes = Image.open(final_img_path)
                
                st.image(image_bytes, caption="المطابقة الاحترافية 100% - استنساخ الوجه", use_container_width=True)
                
                # مسح الملفات المؤقتة للحفاظ على مساحة الموقع
                if os.path.exists(face_path): os.remove(face_path)
                if os.path.exists(scene_path): os.remove(scene_path)

            except Exception as e:
                # هذا هو الجزء الذي كان يفتقده الكود (قفل بلوك الـ try)
                st.error(f"حصلت مشكلة تقنية: {e}")
                # تنظيف الملفات حتى في حالة الخطأ
                if 'face_path' in locals() and os.path.exists(face_path): os.remove(face_path)
                if 'scene_path' in locals() and os.path.exists(scene_path): os.remove(scene_path)
