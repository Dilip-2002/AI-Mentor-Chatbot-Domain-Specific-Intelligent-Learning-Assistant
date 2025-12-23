import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


st.set_page_config(page_title="🤖 AI Chatbot Mentor", layout="centered")

# Session state
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🤖 AI Chatbot Mentor")
st.write("Your personalized AI learning assistant")

module = st.selectbox(
    "Select Learning Module",
    [
        "Python",
        "SQL",
        "Power BI",
        "Exploratory Data Analysis (EDA)",
        "Machine Learning",
        "Deep Learning",
        "Generative AI",
        "Agentic AI",
    ],
)

mentor_experience = st.number_input(
    "Select Mentor Experience (Years)",
    min_value=1,
    max_value=50,
    step=1,
)

if st.button("🚀 Start Mentoring Session", type="primary"):
    st.session_state.chat_started = True
    st.session_state.chat_history = []

if st.session_state.chat_started:

    st.subheader(f"Welcome to {module} AI Mentor")
    st.write(
        f"I am your dedicated **{module} mentor** with **{mentor_experience} year(s) of experience**."
    )

    for role, msg in st.session_state.chat_history:
        st.chat_message(role).write(msg)

    user_question = st.chat_input("Type your query...")

    if user_question:
        st.chat_message("user").write(user_question)
        st.session_state.chat_history.append(("user", user_question))

        system_prompt = f"""
You are an AI Mentor with {mentor_experience} years of experience.
You ONLY answer questions related to the module: {module}.

Rules:
- If the question is NOT related to {module}, reply exactly:
  "Sorry, I don’t know about this question. Please ask something related to the selected module : {module}."
- Keep answers educational, structured, and clear.
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{question}"),
            ]
        )

        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.6
        )

        chain = prompt | model
        response = chain.invoke({"question": user_question}).content

        st.session_state.chat_history.append(("assistant", response))
        st.chat_message("assistant").write(response)

    st.divider()
    st.subheader("📥 Download Conversation")

    def create_txt(chat):
        path = "chat_history.txt"
        with open(path, "w", encoding="utf-8") as f:
            for role, msg in chat:
                f.write(f"{role.upper()}: {msg}\n\n")
        return path

    def create_pdf(chat):
        path = "chat_history.pdf"
        styles = getSampleStyleSheet()
        story = []
        for role, msg in chat:
            story.append(Paragraph(f"<b>{role.upper()}:</b><br/>{msg}", styles["Normal"]))
        SimpleDocTemplate(path).build(story)
        return path

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Download TXT"):
            with open(create_txt(st.session_state.chat_history), "rb") as f:
                st.download_button("Download TXT", f, file_name="chat_history.txt")

    with col2:
        if st.button("Download PDF"):
            with open(create_pdf(st.session_state.chat_history), "rb") as f:
                st.download_button("Download PDF", f, file_name="chat_history.pdf")

    with col3:
        if st.button("Close Chat"):
            st.session_state.chat_started = False
            st.session_state.chat_history = []
            st.rerun()
