import os
import streamlit as st
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(
    page_title="المساعد الذكي لإدارة الأعمال والمحاسبة",
    page_icon="📚",
    layout="centered"
)

# التحقق من مفتاح الـ API وتكوينه
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ برجاء إضافة مفتاح الـ API الخاص بـ Google Gemini في إعدادات Streamlit Secrets تحت اسم GEMINI_API_KEY.")
else:
    genai.configure(api_key=api_key)

# تخصيص واجهة المستخدم
st.markdown("""
    <h2 style='text-align: right; direction: rtl;'>📚 مساعدك الذكي لتحليل وملخصات إدارة الأعمال والمحاسبة</h2>
    <p style='text-align: right; direction: rtl; color: #555;'>
    مرحباً بكِ! يمكنك هنا طرح الأسئلة، أو <b>رفع صور المسائل المحاسبية، أو ملفات الـ PDF</b> ليقوم بتحليلها، تلخيصها، وشرحها بدقة، مع وضع أسئلة تدريبية.
    </p>
    <hr>
""", unsafe_allow_html=True)

# مكان مخصص لرفع الملفات أو الصور في الشريط الجانبي أو الواجهة
st.sidebar.header("📁 مرفقات الملفات والصور")
uploaded_file = st.sidebar.file_uploader(
    "ارفعي ملف PDF، مستند، أو صورة (مسألة/رسم بياني)", 
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

# تهيئة الذاكرة المؤقتة للرسائل في الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال أو المدخلات من المستخدم
prompt = st.chat_input("اطرحي سؤالاً، أو اطلبي تلخيص الملف المرفق، أو إنشاء أسئلة...")

if prompt or uploaded_file:
    # تجهيز محتوى الرسالة للعرض
    user_content = prompt if prompt else "تم رفع ملف/صورة للتحليل والشرح."
    if uploaded_file:
        user_content += f" *(ملف مرفق: {uploaded_file.name})*"

    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        st.markdown(user_content)

    try:
        # إعداد النموذج
        generation_config = {
            "temperature": 0.3,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="أنت خبير محترف وأستاذ أكاديمي في المحاسبة، المالية، وتكنولوجيا الإدارة. مهمتك تحليل الملفات أو الصور المرفقة بدقة، تقديم ملخصات شاملة، شرح المفاهيم بوضوح باللغة العربية، وتوليد أسئلة اختبارية (Quiz) لتقييم الفهم عند الطلب."
        )

        # تجهيز المدخلات للنموذج (سواء نص أو ملفات مرفقة)
        content_parts = []
        
        if prompt:
            content_parts.append(prompt)
        else:
            content_parts.append("قومي بتحليل هذا الملف أو الصورة، لخصيه، واشرحي أهم النقاط المحاسبية أو الإدارية فيه بوضوح.")

        # معالجة الملف المرفق إذا وجد
        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type
            content_parts.append({"mime_type": mime_type, "data": file_bytes})

        with st.spinner("جاري تحليل الملف والتفكير في الإجابة... 🤖"):
            response = model.generate_content(content_parts)
            response_text = response.text

        # عرض رد المساعد وحفظه
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        error_msg = f"حدث خطأ أثناء معالجة الطلب: {e}"
        st.error(error_msg)
        
