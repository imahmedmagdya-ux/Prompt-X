import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import requests

st.set_page_config(page_title="Prompt-X: استنساخ العوالم", page_icon="🔎", layout="centered")

st.title("🔎 Prompt-X: استنساخ العوالم!")
st.write("عيش الخيال وخليه واقع 🚀")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.warning("جاري تجهيز الموقع...")

col1, col2 = st.columns(2)

with col1:
    scene_file = st.file_uploader("🖼️ ارفع المشهد المستهدف", type=["jpg", "jpeg", "png"])
    if scene_file:
        st.image(scene_file, caption="المشهد", use_container_width=True)

with col2:
    face_file = st.file_uploader("🧑 ارفع صورتك الشخصية", type=["jpg", "jpeg", "png"])
    if face_file:
        st.image(face_file, caption="الوجه", use_container_width=True)

if st.button("🚀 اخلق هذا العالم!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري استنساخ ملامحك ورسم العالم الجديد... ⏳"):
            try:
                gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                
                face_image = Image.open(face_file)
                face_prompt = "Analyze this person's facial features strictly and accurately in one English sentence. Describe their approximate age, skin tone, glasses (if any), hair, and expression. Start with: 'A person with...'"
                face_desc = gemini_model.generate_content([face_prompt, face_image]).text.strip()
                
                scene_image = Image.open(scene_file)
                scene_prompt = "Analyze this environment, lighting, and mood accurately in one English sentence. Do NOT describe the people, only the scene and the atmosphere."
                scene_desc = gemini_model.generate_content([scene_prompt, scene_image]).text.strip()
                
                face_desc = face_desc.replace('.', '').replace('\n', ' ')
                scene_desc = scene_desc.replace('.', '').replace('\n', ' ')
                
                final_prompt = f"A breathtaking photorealistic cinematic masterpiece of {face_desc}, wearing dark epic clothing, standing confidently in {scene_desc}. 8k resolution, dramatic lighting, highly detailed, Unreal Engine 5 render, award winning photography"
                
                encoded_prompt = urllib.parse.quote(final_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    st.success("تم تخليق العالم بنجاح! 🎉")
                    st.balloons()
                    
                    st.subheader("إنت في العالم الجديد:")
                    st.image(response.content, caption="الصورة المستنسخة", use_container_width=True)
                    
                    with st.expander("شوف الذكاء الاصطناعي شاف صورتك إزاي (البرومبت السري):"):
                        st.code(final_prompt, language="text")
                else:
                    st.error("حصل ضغط على السيرفر لحظة الرسم، ارجع دوس على الزرار وجرب كمان مرة.")
                    
            except Exception as e:
                st.error(f"حصلت مشكلة صغيرة: {e}")
