import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import base64
import io

st.set_page_config(page_title="Prompt-X: انقل وجهك!", page_icon="🧑‍🎤", layout="centered")

st.title("🧑‍🎤 Prompt-X: انقل وجهك لأي عالم!")
st.write("ارفع صورتين: المشهد اللي بتحلم بيه، وصورتك الشخصية، وسيب الذكاء الاصطناعي يعمل السحر (100 محاولة مجانية يومياً)!")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    segmind_api_key = st.secrets["SEGMIND_API_KEY"]
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
        with st.spinner("جاري تحليل المشهد ودمج العوالم... ⏳"):
            try:
                scene_image = Image.open(scene_file)
                gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                
                scene_analysis_prompt = """
                أنت خبير تصوير. حلل هذه الصورة بدقة لإضاءتها وألوانها والبيئة.
                اكتب Prompt باللغة الإنجليزية يصف هذه البيئة. لا تصف الأشخاص، صف فقط المشهد والملابس.
                اكتب البرومبت كسطر واحد فقط.
                """
                gemini_response = gemini_model.generate_content([scene_analysis_prompt, scene_image])
                base_prompt = gemini_response.text.strip()
                
                face_image = Image.open(face_file)
                buffered = io.BytesIO()
                face_image.thumbnail((800, 800)) 
                face_image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                final_prompt = f"A photorealistic portrait of a man img, {base_prompt}, cinematic lighting, 8k resolution, highly detailed"
                
                url = "https://api.segmind.com/v1/photomaker"
                data = {
                    "prompt": final_prompt,
                    "negative_prompt": "nsfw, generic face, badly drawn, distorted, low quality",
                    "input_image": img_str,
                    "num_inference_steps": 25,
                    "guidance_scale": 7,
                    "style_name": "(No style)"
                }
                
                response = requests.post(url, json=data, headers={'x-api-key': segmind_api_key})
                
                if response.status_code == 200:
                    st.success("تم التوليد بنجاح! 🎉 رصيدك المجاني شغال بكفاءة.")
                    st.balloons()
                    st.subheader("إنت دلوقتي في العالم الجديد:")
                    st.image(response.content, caption="الصورة النهائية", use_container_width=True)
                else:
                    st.error(f"حصل خطأ في التوليد: {response.text}")
                    
            except Exception as e:
                st.error(f"تفاصيل المشكلة: {e}")
