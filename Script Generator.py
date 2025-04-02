import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# Parameters and follow-up prompts
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

def collect_parameters(user_idea):
    convo = model.start_chat(history=[
        {"role": "user", "parts": [f"My idea is: {user_idea}"]},
        {"role": "model", "parts": ["Great! Let's collect a few more details."]},
    ])

    result = {}
    for param, prompt in parameters.items():
        print(f"\n🤖 {prompt}")
        user_input = input("🧑 Your answer (press Enter to skip): ")

        if user_input.strip():
            result[param] = user_input.strip()
        else:
            # Let Gemini pick a suitable default based on the idea
            ai_response = convo.send_message(f"Based on the idea: '{user_idea}', what would be a suitable value for '{param}'?")
            result[param] = clean_answer(param, ai_response.text)

    return result

def generate_scripts(idea, details):
    num_videos = int(details["number_of_videos"])
    script_convo = model.start_chat()

    print("\n🎬 Generating video scripts...\n")
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

def main():
    print("🎥 Welcome to the AI Video Scenario Agent!")
    user_idea = input("🧠 What's your video idea?\n")

    details = collect_parameters(user_idea)

    print("\n✅ Clean Video Scenario:")
    for k, v in details.items():
        print(f"{k.replace('_', ' ').title()}: {v}")

    scripts = generate_scripts(user_idea, details)

    print("\n📜 Video Scripts:\n")
    for title, script in scripts.items():
        print(f"\n--- {title} ---\n{script}\n")

    # Save to JSON
    with open("video_scenario_output.json", "w") as f:
        json.dump({"details": details, "scripts": scripts}, f, indent=4)

    print("\n💾 Output saved to video_scenario_output.json")

if __name__ == "__main__":
    main()