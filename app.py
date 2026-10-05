import time
import streamlit as st
from google import genai
from google.genai import types


# =========================================================
# M-MIS Study AI
# Intelligent Study Assistant for MIS & Business Administration
# =========================================================

st.set_page_config(
    page_title="M-MIS Study AI",
    page_icon="🎓",
    layout="wide",
)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are M-MIS Study AI, an academic study assistant specialized in:
- Management Information Systems (MIS)
- Business Administration
- Management
- Information Systems
- Business Technology

ACADEMIC ACCURACY RULES:
1. When a document is provided, treat the uploaded document as the primary
   source for questions about that document.
2. NEVER invent a fact and claim that it came from the uploaded material.
3. If the answer cannot be found or reliably inferred from the uploaded
   material, explicitly say:
   "This information is not clearly stated in the uploaded material."
4. Clearly distinguish between information directly stated in the material,
   reasonable inferences, and general academic knowledge.
5. When answering questions about the uploaded material, mention the relevant
   page/section when the model can reliably identify it.
6. Preserve important English academic terminology and explain it in Arabic
   when the user asks for Arabic.
7. Do not change definitions from the source merely to make them simpler.
   You may explain them in simpler language after giving the accurate idea.
8. For summaries, preserve important definitions, relationships,
   classifications, processes, and examples.
9. For generated questions, questions MUST be based on the uploaded material.
10. If the source material is ambiguous, incomplete, or contradictory,
    say so instead of guessing.
11. Never present uncertainty as certainty.
12. The user is studying for university exams, so prioritize factual accuracy
    over creativity.

Answer in Arabic by default while keeping important English terms.
"""

# =========================================================
# Gemini Client
# =========================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ لم يتم العثور على GEMINI_API_KEY. "
        "أضيفي المفتاح داخل Streamlit Secrets."
    )
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"حدث خطأ أثناء تشغيل Gemini: {e}")
    st.stop()


# =========================================================
# Session State
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


# =========================================================
# Gemini helper
# =========================================================

def ask_gemini(prompt, uploaded_file=None):
    """Send a prompt to Gemini, optionally with an uploaded file."""

    contents = []

    if uploaded_file:
        contents.append(
            types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type,
            )
        )

    contents.append(types.Part.from_text(text=prompt))

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.1,
        ),
    )

    if not response.text:
        raise RuntimeError("لم يرجع Gemini نصًا في الاستجابة.")

    return response.text


# =========================================================
# Sidebar
# =========================================================

st.sidebar.title("🎓 M-MIS Study AI")

st.sidebar.markdown(
    """
**Intelligent Study Assistant**

متخصص في:
- Management Information Systems
- Business Administration
- Management
"""
)

st.sidebar.divider()

uploaded = st.sidebar.file_uploader(
    "📚 Upload Study Material",
    type=["pdf", "txt", "png", "jpg", "jpeg"],
    help="ارفعي PDF أو صورة أو ملف TXT.",
)

# =========================================================
# Upload material to Gemini
# =========================================================

if uploaded is not None:
    if uploaded.name != st.session_state.uploaded_file_name:
        with st.sidebar:
            with st.spinner("جاري رفع الملف إلى Gemini..."):
                try:
                    uploaded_file = client.files.upload(
                        file=uploaded.getvalue(),
                        config=types.UploadFileConfig(
                            display_name=uploaded.name,
                            mime_type=uploaded.type,
                        ),
                    )

                    # Wait for Gemini to finish processing the file.
                    for _ in range(60):
                        file_info = client.files.get(name=uploaded_file.name)
                        state = getattr(file_info, "state", None)

                        if state is None:
                            break

                        state_name = str(state)

                        if "PROCESSING" not in state_name:
                            break

                        time.sleep(2)

                    st.session_state.uploaded_file = file_info
                    st.session_state.uploaded_file_name = uploaded.name
                    st.session_state.messages = []

                    st.success("✅ تم رفع المادة بنجاح!")

                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء رفع الملف:\n\n{e}")


# =========================================================
# Header
# =========================================================

st.title("🎓 M-MIS Study AI")

st.subheader(
    "Intelligent Study Assistant for "
    "Management Information Systems & Business Administration"
)

st.caption(
    "ارفعي المادة ثم استخدمي Explain أو Summarize أو اسألي عن محتوى الملف."
)

if st.session_state.uploaded_file:
    st.info(
        f"📄 المادة الحالية: **{st.session_state.uploaded_file_name}**"
    )
else:
    st.warning(
        "📚 ارفعي محاضرة أو PDF أو صورة من القائمة الجانبية للبدء."
    )


# =========================================================
# Quick actions
# =========================================================

st.markdown("### ⚡ Study Tools")

col1, col2, col3 = st.columns(3)

with col1:
    explain_button = st.button("🧠 Explain", use_container_width=True)

with col2:
    summarize_button = st.button("📝 Summarize", use_container_width=True)

with col3:
    key_points_button = st.button("🎯 Key Points", use_container_width=True)


# =========================================================
# Explain
# =========================================================

if explain_button:
    if not st.session_state.uploaded_file:
        st.warning("ارفعي المادة أولًا.")
    else:
        prompt = """
Explain the uploaded study material in Arabic.

Requirements:
- Explain the concepts step by step.
- Keep important English academic terminology.
- Preserve the original meaning of definitions.
- Give simple examples only when consistent with the material.
- Clearly identify information directly stated in the material.
- Do not invent information.
- If an important concept is not clear in the material, say so.
"""

        with st.spinner("🧠 جاري شرح المادة..."):
            try:
                answer = ask_gemini(
                    prompt,
                    st.session_state.uploaded_file,
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


# =========================================================
# Summarize
# =========================================================

if summarize_button:
    if not st.session_state.uploaded_file:
        st.warning("ارفعي المادة أولًا.")
    else:
        prompt = """
Create an accurate academic summary of the uploaded material.

Structure the answer as:
1. Main topic
2. Important definitions
3. Main concepts
4. Classifications
5. Processes or steps
6. Important relationships
7. Important examples
8. Exam-focused points

Do not remove important information simply to make the summary shorter.
Do not invent information that is not present in the material.
"""

        with st.spinner("📝 جاري إعداد الملخص..."):
            try:
                answer = ask_gemini(
                    prompt,
                    st.session_state.uploaded_file,
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


# =========================================================
# Key Points
# =========================================================

if key_points_button:
    if not st.session_state.uploaded_file:
        st.warning("ارفعي المادة أولًا.")
    else:
        prompt = """
Extract the most important points from the uploaded study material.

Focus on information that is likely to be important for understanding
the subject and preparing for an exam.

Include:
- Important definitions
- Key terms
- Classifications
- Differences between concepts
- Processes
- Relationships
- Important examples

Use concise bullet points.
Only use information supported by the uploaded material.
"""

        with st.spinner("🎯 جاري استخراج أهم النقاط..."):
            try:
                answer = ask_gemini(
                    prompt,
                    st.session_state.uploaded_file,
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"حدث خطأ: {e}")


# =========================================================
# Chat history
# =========================================================

st.markdown("### 💬 Ask About Your Material")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# Chat
# =========================================================

prompt = st.chat_input("اسألي عن المحاضرة...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.uploaded_file:
        answer = (
            "📚 ارفعي المادة أولًا، وبعدها أقدر أجاوبك "
            "بناءً على محتواها."
        )
    else:
        enhanced_prompt = f"""
The student asks:

{prompt}

Answer the question using the uploaded material as the primary source.

Academic accuracy requirements:
- Do not invent information.
- If the answer is not clearly supported by the material, explicitly say so.
- If you use general academic knowledge to clarify something,
  label it clearly as general knowledge.
- If possible, identify the relevant page or section.
- Keep important English terminology.
- Answer in clear Arabic unless English terminology is required.
"""

        with st.spinner("🤖 جاري تحليل المادة والإجابة..."):
            try:
                answer = ask_gemini(
                    enhanced_prompt,
                    st.session_state.uploaded_file,
                )
            except Exception as e:
                answer = f"❌ حدث خطأ أثناء الحصول على الإجابة:\n\n{e}"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )


# =========================================================
# Accuracy notice
# =========================================================

st.divider()

st.caption(
    "⚠️ Academic accuracy: M-MIS Study AI is designed to answer from "
    "uploaded study materials when available. AI can still make mistakes, "
    "so verify critical definitions and exam requirements against your "
    "official course material."
)
