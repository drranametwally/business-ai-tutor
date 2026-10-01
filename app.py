import time
import streamlit as st
from google import genai

# إعداد الصفحة
st.set_page_config(
    page_title="مساعد جمناي الذكي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 مساعد جمناي الذكي")
st.write("اسألي في أي مجال وسيتم الرد بدقة واحترافية.")

# جلب مفتاح الـ API من إعدادات Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ يرجى ضبط مفتاح GEMINI_API_KEY في إعدادات Secrets الخاصة بتطبيقك على Streamlit.")
else:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"خطأ في تهيئة الاتصال: {e}")
        client = None

    # حفظ الرسائل لعرضها على الشاشة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # استقبال السؤال أو الطلب من المستخدم
    if prompt := st.chat_input("اكتبي سؤالك أو استفسارك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if client:
            response_text = None
            # قائمة الموديلات المتاحة للتجربة بالترتيب لو واحد عليه ضغط
            models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            
            with st.spinner("جاري الاتصال بـ Gemini... 🤖"):
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        response_text = response.text
                        break # لو نجح، اخرج من اللوب فوراً
                    except Exception as e:
                        # لو حصل خطأ ضغط، جرب الموديل اللي بعده أو انتظر ثانية
                        continue

            if response_text:
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("⚠️ السيرفر عليه ضغط حالياً (503). انتظري ثواني واكتبي سؤالك تاني وهيوصل فوراً!")
        else:
            st.error("العميل غير متصل، يرجى التأكد من مفتاح الـ API.")
            
