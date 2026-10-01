import streamlit as st
from google import genai

# إعداد صفحة المتصفح
st.set_page_config(
    page_title="مساعد إدارة الأعمال والمحاسبة الذكي", page_icon="📈", layout="centered"
)

# تخصيص واجهة المستخدم بالعنوان والمقدمة
st.title("📈 مساعدك الذكي لإدارة الأعمال والمحاسبة")
st.markdown(
    "مرحباً بكِ! هذا المساعد مصمم خصيصاً لمساعدتك في فهم نظريات الإدارة، حل"
    " المسائل المحاسبية، وتبسيط المصطلحات المعقدة."
)

# جلب مفتاح الـ API بأمان من إعدادات الموقع
try:
  API_KEY = st.secrets["API_KEY"]
except Exception:
  API_KEY = "YOUR_API_KEY"

# التحقق من إدخال المفتاح
if API_KEY == "YOUR_API_KEY":
  st.warning(
      "⚠️ من فضلك قومي بإضافة مفتاح الـ API في إعدادات Secrets على Streamlit"
      " لكي يعمل البوت."
  )

# إعداد عميل الذكاء الاصطناعي وتوجيه البوت ليتخصص في المجال
system_instruction = (
    "أنت خبير وأستاذ أكاديمي متخصص في إدارة الأعمال، المحاسبة المالية، والتكاليف."
    " مهمتك مساعدة الطالبة في فهم المناهج، حل التمارين خطوة بخطوة، وشرح"
    " المصطلحات الإدارية والمحاسبية بأسلوب مبسط وواضح مع ضرب أمثلة عملية."
)

try:
  client = genai.Client(api_key=API_KEY)
except Exception:
  client = None

# حفظ سجل المحادثة
if "messages" not in st.session_state:
  st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# صندوق إدخال الرسائل من المستخدم
if prompt := st.chat_input(
    "اكتبي سؤالك هنا (مثلاً: ما هو الفرق بين أساس الاستحقاق والأساس النقدي؟)"
):
  if API_KEY == "YOUR_API_KEY":
    st.error("الرجاء إعداد مفتاح الـ API أولاً لكي يتم إرسال الرسالة.")
  else:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("جاري التفكير وتحليل السؤال..."):
        try:
          chat = client.chats.create(
              model="gemini-3.8-flash",
              config=genai.types.GenerateContentConfig(
                  system_instruction=system_instruction, temperature=0.3
              ),
          )
          response = chat.send_message(prompt)
          bot_response = response.text

          st.markdown(bot_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": bot_response}
          )
        except Exception as e:
          st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
          
