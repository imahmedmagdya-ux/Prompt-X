import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import time

# 1. تظبيط شكل الصفحة
st.set_page_config(page_title="Prompt-X: استنساخ العوالم", page_icon="🪄", layout="centered")

st.title("🪄 Prompt-X: استنساخ العوالم!")
st.write("النسخة الاحترافية (Stable Diffusion XL): رسم سينمائي فائق الجودة، مجاني ومستقر 100% 🚀")

# 2. ربط المفاتيح (جوجل و Hugging Face)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    hf_token = st.secrets["HF_TOKEN"]
except Exception as e:
    st.warning("جاري تجهيز الموقع... تأكد من إعدادات المفاتيح السرية.")

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
if st.button("🚀 اخلق هذا العالم!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري استنساخ ملامحك ورسم العالم الجديد... ⏳ (ممكن تاخد 30 ثانية)"):
            try:
                # --- خطوة الحماية: تصغير الصور لتوفير باقة جوجل ---
                face_image = Image.open(face_file)
                face_image.thumbnail((512, 512)) 
                scene_image = Image.open(scene_file)
                scene_image.thumbnail((512, 512)) 
                
                # --- الخطوة أ: تحليل المشهد والوجه (Gemini) ---
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                
                face_prompt = "Analyze this person's facial features strictly and accurately in one English sentence. Describe their approximate age, skin tone, glasses (if any), hair, and expression. Start with: 'A person with...'"
                face_desc = gemini_model.generate_content([face_prompt, face_image]).text.strip()
                
                scene_prompt = "Analyze this environment, lighting, and mood accurately in one English sentence. Do NOT describe the people, only the scene and the atmosphere."
                scene_desc = gemini_model.generate_content([scene_prompt, scene_image]).text.strip()
                
                # --- الخطوة ب: بناء البرومبت النهائي ---
                final_prompt = f"A breathtaking photorealistic cinematic masterpiece of {face_desc}, wearing dark epic clothing, standing confidently in {scene_desc}. 8k resolution, dramatic lighting, highly detailed, Unreal Engine 5 render"
                
                # --- الخطوة ج: الرسم عبر السيرفر الرسمي لـ Hugging Face ---
                API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": f"Bearer {hf_token}"}
                payload = {"inputs": final_prompt}
                
                response = requests.post(API_URL, headers=headers, json=payload)
                
                # معالجة حالة "الموديل بيحمل" (بيحصل أحياناً في السيرفرات المجانية)
                if response.status_code == 503:
                    st.info("السيرفر بيسخن المكنة (بيحمل الموديل).. هنستنى 15 ثانية ونحاول تاني تلقائياً ⏳")
                    time.sleep(15)
                    response = requests.post(API_URL, headers=headers, json=payload)
                
                # --- الخطوة د: عرض النتيجة ---
                if response.status_code == 200:
                    st.success("تم تخليق العالم بنجاح! 🎉")
                    st.balloons()
                    
                    st.subheader("إنت في العالم الجديد:")
                    st.image(response.content, caption="الصورة المستنسخة", use_container_width=True)
                    
                    with st.expander("البرومبت السري المستخدم:"):
                        st.code(final_prompt, language="text")
                else:
                    st.error(f"حصل خطأ في الرسم: {response.text}")
                    
            except Exception as e:
                st.error(f"حصلت مشكلة: {e}")
