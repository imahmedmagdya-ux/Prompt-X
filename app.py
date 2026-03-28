import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import requests
import random # ضفنا دي عشان توليد أرقام عشوائية للصور

# 1. تظبيط شكل الصفحة
st.set_page_config(page_title="Prompt-X: استنساخ العوالم", page_icon="🚀", layout="centered")

st.title("🚀 Prompt-X: استنساخ العوالم!")
st.write("النسخة المستقرة والموفرة للطاقة: تعمل بكفاءة عالية بدون استهلاك الباقة 🚀")

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
if st.button("🚀 اخلق هذا العالم!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري استنساخ ملامحك ورسم العالم الجديد... ⏳ (ممكن تاخد 20 ثانية)"):
            try:
                # --- خطوة الحماية: تصغير الصور قبل إرسالها لجوجل لتوفير الباقة (Tokens) ---
                face_image = Image.open(face_file)
                face_image.thumbnail((512, 512)) # تصغير الصورة
                
                scene_image = Image.open(scene_file)
                scene_image.thumbnail((512, 512)) # تصغير الصورة
                
                # --- الخطوة أ: تحليل المشهد والوجه باستخدام Gemini النسخة المستقرة ---
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                
                face_prompt = "Analyze this person's facial features strictly and accurately in one English sentence. Describe their approximate age, skin tone, glasses (if any), hair, and expression. Start with: 'A person with...'"
                face_desc = gemini_model.generate_content([face_prompt, face_image]).text.strip()
                
                scene_prompt = "Analyze this environment, lighting, and mood accurately in one English sentence. Do NOT describe the people, only the scene and the atmosphere."
                scene_desc = gemini_model.generate_content([scene_prompt, scene_image]).text.strip()
                
                # تنظيف البرومبت
                face_desc = face_desc.replace('.', '').replace('\n', ' ')
                scene_desc = scene_desc.replace('.', '').replace('\n', ' ')
                
                # --- الخطوة ب: بناء البرومبت النهائي ---
                final_prompt = f"A breathtaking photorealistic cinematic masterpiece of {face_desc}, wearing dark epic clothing, standing confidently in {scene_desc}. 8k resolution, dramatic lighting, highly detailed, Unreal Engine 5 render, award winning photography"
                
                # --- الخطوة ج: التنكر وتحميل الصورة ---
                encoded_prompt = urllib.parse.quote(final_prompt)
                
                # ضفنا رقم عشوائي (Seed) عشان السيرفر يرسم صورة جديدة طازة كل مرة
                random_seed = random.randint(1, 1000000)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={random_seed}"      
                
                # الباسبور المزور (User-Agent) عشان السيرفر يفتكرنا متصفح كروم حقيقي
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                
                # زودنا وقت الانتظار لـ 60 ثانية عشان السيرفر ياخد راحته في الرسم
                response = requests.get(image_url, headers=headers, timeout=60)
                
                # --- الخطوة د: عرض النتيجة ---
                if response.status_code == 200:
                    st.success("تم تخليق العالم بنجاح! 🎉")
                    st.balloons()
                    
                    st.subheader("إنت في العالم الجديد:")
                    st.image(response.content, caption="الصورة المستنسخة", use_container_width=True)
                    
                    with st.expander("البرومبت السري المستخدم:"):
                        st.code(final_prompt, language="text")
                else:
                    st.error(f"الحارس بتاع السيرفر لسه قافش شوية (كود الخطأ: {response.status_code}). جرب تاني كمان لحظات.")
                    
            except Exception as e:
                st.error(f"حصلت مشكلة: {e}")
