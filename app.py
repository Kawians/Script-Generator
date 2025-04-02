import os
import re
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

parameters = {
    "number_of_videos": "How many videos would you like?",
    "duration_minutes": "What should be the duration of each video (in minutes)?",
    "graphic_type": "What graphic style do you prefer? (realistic, animated, imaginative)",
    "video_style": "What is the video style? (animated video, motion pictures, steady pictures)",
    "audience": "Who is your target audience? (e.g. general, children aged 6, etc.)"
}

def extract_number(text):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else text

def clean_answer(param, response):
    text = response.strip()
    if param == "number_of_videos" or param == "duration_minutes":
        return extract_number(text)
    elif param in ["graphic_type", "video_style", "audience"]:
        match = re.search(r"(realistic|animated|imaginative|motion pictures|steady pictures|animated video|general|children.*)", text, re.IGNORECASE)
        return match.group().capitalize() if match else text
    return text

def generate_scripts(idea, details):
    num_videos = int(details["number_of_videos"])
    script_convo = model.start_chat()
    scripts = {}
    for i in range(1, num_videos + 1):
        prompt = (
            f"Create a short script for video {i} of a {num_videos}-part video series based on the idea: '{idea}'. "
            f"Each video is {details['duration_minutes']} minutes long, in a {details['graphic_type']} graphic style, "
            f"with a {details['video_style']} format. The audience is: {details['audience']}."
        )
        response = script_convo.send_message(prompt)
        scripts[f"Video {i}"] = response.text.strip()
    return scripts

# Streamlit UI
st.set_page_config(page_title="AI Video Scenario Generator", layout="wide")
st.title("🎬 AI Video Scenario Generator")

user_idea = st.text_area("🧠 Describe your video idea:", height=100)

if user_idea:
    with st.form("video_parameters_form"):
        st.subheader("Optional: Provide additional details or leave blank to let AI decide")
        inputs = {}
        for param, prompt in parameters.items():
            inputs[param] = st.text_input(prompt)
        submitted = st.form_submit_button("Generate Video Scenario")

    if submitted:
        convo = model.start_chat()
        details = {}

        with st.spinner("🤖 Collecting scenario details..."):
            for param, prompt in parameters.items():
                if inputs[param].strip():
                    details[param] = inputs[param].strip()
                else:
                    ai_response = convo.send_message(f"Based on the idea: '{user_idea}', what would be a suitable value for '{param}'?")
                    details[param] = clean_answer(param, ai_response.text)

        st.success("✅ Parameters finalized!")
        st.json(details)

        with st.spinner("🎥 Generating scripts for each video..."):
            scripts = generate_scripts(user_idea, details)

        st.subheader("📜 Generated Scripts:")
        for title, script in scripts.items():
            st.markdown(f"### {title}")
            st.markdown(script)

        # Download JSON
        output = {"idea": user_idea, "details": details, "scripts": scripts}
        st.download_button("💾 Download Full JSON", data=json.dumps(output, indent=4), file_name="video_scenario.json", mime="application/json")
