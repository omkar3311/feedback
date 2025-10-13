import streamlit as st
from supabase import create_client, Client
import pandas as pd
import matplotlib.pyplot as plt
import io
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
ADMIN_USERNAME = st.secrets["ADMIN_USERNAME"]

feedback_questions = {
    "How would you rate the overall session?": ["1 - Poor", "2 - Fair", "3 - Good", "4 - Very Good", "5 - Excellent"],
    "Was the content clear and easy to understand?": ["Yes", "Somewhat", "No"],
    "How engaging was the session?": ["1 - Boring", "2", "3", "4", "5 - Very Engaging"],
    "How was the pace of the session?": ["Too Fast", "Perfect", "Too Slow"],
    "Did you find the topics covered relevant to your learning or career goals?": ["Yes", "Partially", "No"],
    "Before attending this session, how familiar were you with Git and GitHub?": ["Not at all familiar", "Heard of it but never used", "Used a little", "Comfortable using them"],
    "After this session, how confident are you in using Git and GitHub commands?": ["Not Confident", "Somewhat Confident", "Confident", "Very Confident"],
    "Were the live demonstrations or practical examples helpful?": ["Yes, very helpful", "Somewhat helpful", "No, not much"],
    "How useful did you find the hands-on or command-line demonstrations?": ["1 - Not Useful", "2", "3", "4", "5 - Very Useful"],
    "Did this session motivate you to explore version control or open-source contribution further?": ["Yes", "Maybe", "No"],
    "What did you like the most about the session?": ["text"],
    "What could be improved in future sessions?": ["text"],
    "How would you rate the instructor's clarity and explanation of Git/GitHub commands?": [ "1 - Poor", "2 - Fair", "3 - Good", "4 - Very Good", "5 - Excellent"],
    "Which Topics would you like to learn next?": ["AIML","JAVA-DEVELOPMENT","DOCKER"]
}

st.set_page_config(page_title="Git & GitHub Feedback", page_icon="💬", layout="wide")

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("💬 Git & GitHub Feedback Form")
st.markdown("We value your feedback! Please share your honest thoughts about the session. 🙌")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("**Your Name(optional)**")
    with col2:
        year = st.selectbox("**Year**", ["Select", "FY", "SY", "TY", "BTECH"], index=0)
        branch = st.selectbox("**Branch**", ["Select", "CSE", "AIDS"], index=0)

if name.strip().lower() == ADMIN_USERNAME.lower():
    st.session_state.is_admin = True
else:
    st.session_state.is_admin = False

if st.session_state.is_admin:
    st.header("📊 Feedback Analytics Dashboard")
    try:
        data = supabase.table("feedback").select("*").execute()
        df = pd.DataFrame(data.data)
        if df.empty:
            st.warning("No feedback data available yet.")
        else:
            responses_df = df["responses"].apply(pd.Series)
            full_df = pd.concat([df.drop(columns=["responses"]), responses_df], axis=1)
            st.success(f"Loaded {len(full_df)} responses ✅")
            csv_buffer = io.StringIO()
            full_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Feedback Data (CSV)",
                data=csv_buffer.getvalue(),
                file_name="feedback_responses.csv",
                mime="text/csv"
            )
            st.divider()
            q_list = list(feedback_questions.items())
            for i in range(0, len(q_list), 2):
                col1, col2 = st.columns(2)
                for col, idx in zip([col1, col2], [i, i + 1]):
                    if idx < len(q_list):
                        question, options = q_list[idx]
                        with col:
                            st.subheader(question)
                            if options == ["text"]:
                                text_responses = full_df[question].dropna()
                                if len(text_responses) == 0:
                                    st.info("No responses yet.")
                                else:
                                    st.write("🗣 Sample Responses:")
                                    st.write(text_responses)
                            else:
                                counts = full_df[question].value_counts().sort_index()
                                fig, ax = plt.subplots()
                                counts.plot(kind="bar", ax=ax)
                                ax.set_ylabel("Count")
                                ax.set_xlabel("Options")
                                ax.set_title(question)
                                st.pyplot(fig)
                st.divider()
    except Exception as e:
        st.error(f"Error loading feedback: {e}")

else:
    with st.form("feedback_form", clear_on_submit=True):
        st.divider()
        responses = {}
        for question, options in feedback_questions.items():
            st.markdown(f"**{question}**")
            if options == ["text"]:
                responses[question] = st.text_area("Your answer(optional):", key=question)
            else:
                responses[question] = st.radio("", options, key=question, index=None)
            st.write("---")
        submitted = st.form_submit_button("✅ Submit Feedback")

    if submitted:
        if year == "Select" and branch == "Select":
            st.warning("⚠️ Please select your **Year** and **Branch** before submitting.")
        elif year == "Select":
            st.warning("⚠️ Please select your **Year** before submitting.")
        elif branch == "Select":
            st.warning("⚠️ Please select your **Branch** before submitting.")
        else:
            data = {
                "name": name.strip() if name else None,
                "year": year if year != "Select" else None,
                "branch": branch if branch != "Select" else None,
                "responses": responses
            }
            try:
                supabase.table("feedback").insert(data).execute()
                st.success("🎉 Thank you for your valuable feedback!")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving feedback: {e}")
