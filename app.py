import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Prompt-X | هندسة الخيال", page_icon="🪄", layout="centered")

st.title("🔎 Prompt-X: استخرج الكود السري لأي صورة")
st.write("ارفع أي صورة، والذكاء الاصطناعي هيحللها ويكتبلك البرومبت السحري بتاعها!")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.warning("جاري تجهيز الموقع... ⏳")

uploaded_file = st.file_uploader("اسحب وارمي الصورة هنا، أو اضغط للاختيار...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة اللي رفعناها", use_container_width=True)
    
    if st.button("🚀 توليد الكود السري"):
        with st.spinner("جاري المسح بالليزر وتحليل تفاصيل الصورة... ⏳"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt_instructions = "أنت خبير في تصميم الصور بالذكاء الاصطناعي. حلل هذه الصورة بدقة شديدة، واكتب Prompt باللغة الإنجليزية يمكن استخدامه في أدوات مثل Midjourney لإعادة إنتاج صورة مشابهة تماماً. ركز على الإضاءة، الألوان، زاوية الكاميرا، والأسلوب الفني. اكتب الكود مباشرة بدون مقدمات."
                
                response = model.generate_content([prompt_instructions, image])
                
                st.success("تم التحليل بنجاح! 🎉")
                st.subheader("الكود السري (Prompt):")
                st.code(response.text, language="text")
                
            except Exception as e:
                st.error("حصلت مشكلة صغيرة، جرب صورة تانية أو تأكد من إعدادات الموقع.")
