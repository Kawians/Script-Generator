import os
import google.generativeai as genai

# Load Gemini API key from environment
genai.configure(api_key=os.getenv("AIzaSyBXQe_hhNWBIvOGInZ_NzrqWD_Z0KK5wD0"))

# Define required parameters and their follow-up prompts
video_parameters = {
    "how_many_videos": "How many videos would you like to generate?",
    "duration_each_video": "What should be the duration (in minutes) of each video?",
    "graphic_type": "What kind of graphic style do you prefer? (realistic, animated, imaginative)",
    "video_style": "What is the video style? (animated video, motion pictures, steady pictures)",
    "audience": "Who is your target audience? (general content, children of age X, etc.)"
}

# Initialize model
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

def collect_parameters(user_input):
    filled_params = {}
    
    # Start with basic idea from user
    convo = model.start_chat()
    convo.send_message(f"The user has this idea for a video: {user_input}. We want to generate a JSON with the following fields: {list(video_parameters.keys())}.")
    
    for param, prompt in video_parameters.items():
        response = convo.send_message(f"If the user didn't specify the '{param}' earlier, ask them: {prompt}. If they don't care or skip it, use your best guess.")
        
        print(f"\n🤖 {response.text}")
        user_value = input("🧑 Your answer (press Enter to skip): ")
        
        if not user_value.strip():
            # Let Gemini infer if skipped
            response = convo.send_message(f"The user skipped '{param}'. Please choose the most appropriate value based on their idea.")
            user_value = response.text.strip()

        filled_params[param] = user_value
    
    return filled_params

def main():
    print("🎬 Welcome to the AI Video Scenario Generator!")
    user_idea = input("🧠 What's your idea for the video(s)?\n")

    scenario = collect_parameters(user_idea)

    print("\n✅ Generated Scenario JSON:\n")
    import json
    print(json.dumps(scenario, indent=4))

if __name__ == "__main__":
    main()