import streamlit as st
from google import genai

# إعداد الصفحة وتنسيقها
st.set_page_config(
    page_title="مساعد جمناي الذكي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 مساعد جمناي الذكي")
st.write("اسألي في أي مجال (برمجة، علوم، أبحاث، تسويق، لغات...) وسيتم الرد بدقة واحترافية.")

# جلب مفتاح الـ API من إعدادات Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ يرجى ضبط مفتاح GEMINI_API_KEY في إعدادات Secrets الخاصة بتطبيقك على Streamlit.")
else:
    # تهيئة عميل Gemini
    client = genai.Client(api_key=api_key)

    # تهيئة الذاكرة الخاصة بالمحادثة في Streamlit
    if "chat_history" not in st.session_state:
        # بنبدأ بجلسة دردشة حقيقية مع جمناي عشان يفتكر السياق
        st.session_state.chat_history = client.chats.create(model="gemini-2.5-flash")

    # حفظ الرسائل لعرضها على الشاشة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل السابقة على واجهة البرنامج
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # استقبال السؤال أو الطلب من المستخدم
    if prompt := st.chat_input("اكتبي سؤالك أو استفسارك هنا..."):
        # عرض رسالة المستخدم فوراً
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # إرسال الرسالة لجلسة الدردشة النشطة لضمان دقة السياق والرد
            response = st.session_state.chat_history.send_message(prompt)
            response_text = response.text

            # عرض رد جمناي
            with st.chat_message("assistant"):
                st.markdown(response_text)
            
            # حفظ رد المساعد في الذاكرة
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بـ Gemini: {e}")
            
