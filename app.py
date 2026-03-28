import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
import os

st.set_page_config(page_title="Prompt-X: انقل وجهك!", page_icon="🧑‍🎤", layout="centered")

st.title("🧑‍🎤 Prompt-X: انقل وجهك لأي عالم!")
st.write("ارفع صورتين: المشهد اللي بتحلم بيه، وصورتك الشخصية، وسيب الذكاء الاصطناعي يعمل السحر!")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    replicate_client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
except Exception as e:
    st.warning(f"جاري تجهيز الموقع... تأكد من إعدادات الـ APIs. التفاصيل: {e}")

col1, col2 = st.columns(2)

with col1:
    scene_file = st.file_uploader("🖼️ ارفع المشهد المستهدف (Scene)", type=["jpg", "jpeg", "png"])
    if scene_file:
        st.image(scene_file, caption="المشهد المستهدف", use_container_width=True)

with col2:
    face_file = st.file_uploader("🧑 ارفع صورتك الشخصية (Face)", type=["jpg", "jpeg", "png"])
    if face_file:
        st.image(face_file, caption="صورتك الشخصية", use_container_width=True)

if st.button("🚀 انقلني لهذا العالم!"):
    if not scene_file or not face_file:
        st.error("ارجوك، ارفع الصورتين الأول!")
    else:
        with st.spinner("جاري مسح الوجه، تحليل المشهد، ودمج العوالم... ⏳ (ممكن ياخد دقيقة)"):
            try:
                scene_image = Image.open(scene_file)
                gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
                
                scene_analysis_prompt = """
                أنت خبير تصوير ومصمم ذكاء اصطناعي. حلل هذه الصورة بدقة شديدة لإضاءتها، ألوانها، زاوية الكاميرا، والتكوين.
                اكتب Prompt باللغة الإنجليزية يصف هذه البيئة كأنها استوديو تصوير، مع التركيز على جودة الإضاءة الذهبية والظل.
                لا تصف الأشخاص، صف فقط المشهد والملابس التي يرتديها الشخص (مثل العباءة المقنعة).
                اكتب البرومبت مباشرة كسطر واحد من الكلمات المفتاحية.
                """
                
                gemini_response = gemini_model.generate_content([scene_analysis_prompt, scene_image])
                
                base_prompt = gemini_response.text.strip()
                
                face_file.seek(0)
                
                final_prompt = f"A photorealistic, highly detailed portrait of a man img, {base_prompt}, intense cinematic lighting, perfect likeness, high quality"
                
                model_inputs = {
                    "input_image": face_file, 
                    "prompt": final_prompt,
                    "negative_prompt": "nsfw, generic face, blurred, duplicate faces, pose distortion, cartoon, low quality",
                    "num_steps": 40, 
                    "guidance_scale": 5,
                }
                
                model_version = "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
                
                output_url_list = replicate_client.run(model_version, input=model_inputs)
                
                final_image_url = output_url_list[0]
                
                st.success("تم التوليد والمطابقة بنجاح! 🎉")
                st.balloons()
                st.subheader("إنت دلوقتي في العالم الجديد:")
                st.image(final_image_url, caption="الصورة النهائية", use_container_width=True)
                
            except Exception as e:
                st.error(f"حصلت مشكلة صغيرة في التوليد. قولي التفاصيل دي عشان نحلها: {e}")
