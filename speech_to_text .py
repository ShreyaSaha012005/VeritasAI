import os
import time
import speech_recognition as sr
from hugchat import hugchat
from hugchat.login import Login

# HuggingFace credentials
HUGGINGFACE_EMAIL = "kulashrishruti@gmail.com"
HUGGINGFACE_PASS = "Shrumaanvi1512"

# Login to HuggingChat
sign = Login(email=HUGGINGFACE_EMAIL, passwd=HUGGINGFACE_PASS)
cookies = sign.login()
chatbot = hugchat.ChatBot(cookies=cookies)

# Extended timeout and phrase limits
def listen_and_recognize(prompt_text=None, timeout=15, phrase_time_limit=30):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    if prompt_text:
        print(f"\n🗣 {prompt_text}\n")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("🧠 Recognizing...")
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            print("❌ Could not understand the audio.")
        except sr.WaitTimeoutError:
            print("⌛ Timeout reached while waiting for audio.")
        except sr.RequestError:
            print("🚫 Error with the speech recognition service.")
        return None

# Get topic
def get_debate_topic():
    retries = 0
    while retries < 4:
        topic = listen_and_recognize("Please say your debate topic:")
        if topic:
            print(f"🗣 Topic: {topic}")
            return topic
        print(f"❌ Could not get the topic. Attempt {retries + 1} of 4.")
        retries += 1
    print("❌ Too many failed attempts. Exiting.")
    exit()


def get_stance():
    retries = 0
    while retries < 4:
        stance_input = listen_and_recognize("Do you want to argue 'for' or 'against' the topic?")
        if not stance_input:
            print(f"❌ Could not understand your stance. Attempt {retries + 1} of 4.")
            retries += 1
            continue

        stance_input = stance_input.lower()
        print(f"🗣 Detected stance transcript: {stance_input}")

        for_keywords = {"for", "support", "agree", "in favor", "favor", "yeah", "yes", "yep", "sure", "four", "go with", "for it", "i am for", "i'm for", "i support", "i agree", "favour"}
        against_keywords = {"against", "oppose", "disagree", "no", "nay", "not", "object", "against it", "oppose it", "again", "nope", "i'm against", "i am against"}

        # Word-by-word match
        for word in stance_input.split():
            if word in for_keywords:
                print("✅ You are arguing: for")
                return "for"
            elif word in against_keywords:
                print("✅ You are arguing: against")
                return "against"

        # Phrase match fallback
        for phrase in for_keywords:
            if phrase in stance_input:
                print("✅ You are arguing: for")
                return "for"
        for phrase in against_keywords:
            if phrase in stance_input:
                print("✅ You are arguing: against")
                return "against"

        print("❌ Could not confidently detect your stance. Please try again.")
        retries += 1

    print("❌ Too many failed attempts to detect stance. Exiting.")
    exit()


# Get duration in minutes
def get_duration():
    duration_input = listen_and_recognize("Say your debate time in minutes (e.g., say 'five' or 'three'):")
    print(f"🔍 Detected time transcript: {duration_input}")
    words_to_numbers = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "tree": 3, "own": 1, "for": 4
    }
    if duration_input:
        for word, number in words_to_numbers.items():
            if word in duration_input:
                print(f"🕐 Time limit set: {number} minutes")
                return number
    try:
        fallback = int(input("⌨ Couldn't understand. Please type duration in minutes (e.g., 3, 5, 10): "))
        print(f"🕐 Time limit set: {fallback} minutes")
        return fallback
    except ValueError:
        print("❌ Invalid duration. Exiting.")
        exit()

# Generate AI argument based on stance
def generate_ai_argument(topic, stance):
    prompt = f"You are an AI debater. The topic is: '{topic}'. You must strictly argue in {stance.upper()} of the topic. Give your opening statement accordingly."
    print("🤖 Generating opening statement...")
    return chatbot.chat(prompt)

# Debate loop
def debate_loop(topic, stance, duration_minutes):
    end_time = time.time() + duration_minutes * 60
    ai_turn = True
    last_user_input = ""
    user_transcript = []
    ai_transcript = []

    print(f"\n🕒 Debate started! You have {duration_minutes} minutes.\n")

    while time.time() < end_time:
        if ai_turn:
            if last_user_input:
                prompt = (
                    f"You are continuing a DEBATE on the topic: '{topic}'.\n"
                    f"The user is taking the OPPOSITE stance of yours and just said: '{last_user_input}'.\n"
                    f"You are arguing STRICTLY in the '{stance.upper()}' position. Give a rebuttal that DISAGREES with the user's statement.\n"
                    f"Be sharp, logical, and persuasive. DO NOT agree with the user's argument. DO NOT switch sides."
                )
            else:
                prompt = (
                    f"You are an AI debater. The topic is: '{topic}'. You must argue STRICTLY in the '{stance.upper()}' side.\n"
                    f"Begin with a strong, structured, and persuasive opening statement.\n"
                    f"Do NOT acknowledge counterpoints. DO NOT be neutral. Stick fully to the '{stance.upper()}' position."
                )

            ai_response = chatbot.chat(prompt)
            print(f"\n🤖 AI: {ai_response}\n")
            ai_transcript.append(str(ai_response))  # ✅ Ensure it's a string
            input("🔽 Press Enter when you finish reading...")
            ai_turn = False

        else:
            user_input = listen_and_recognize("🎙 Your counter-argument (you have more time now):", timeout=20, phrase_time_limit=35)
            if user_input:
                print(f"🗣 You said: {user_input}")
                user_transcript.append(user_input)  # ✅ Fix: append user input
                last_user_input = user_input
                ai_turn = True
            else:
                print("❌ Could not understand your argument. Skipping your turn...")

    print("\n⏳ Debate time over! Analyzing the debate...\n")

    summary_prompt = (
        f"The topic was: '{topic}'. The AI argued in favor of '{stance.upper()}' and the user argued against it.\n\n"
        f"User's arguments:\n" + "\n".join(user_transcript) + "\n\n"
        f"AI's arguments:\n" + "\n".join(str(msg) for msg in ai_transcript) + "\n\n"
        f"Now, analyze the overall debate. Summarize both sides clearly and fairly. Then give unbiased feedback and assign a score out of 10 for each side based on logical strength, clarity, relevance, and persuasiveness.\n"
        f"Conclude with: 'Final Scores — AI: __/10 | User: __/10'"
    )

    final_summary = chatbot.chat(summary_prompt)
    print(f"🧾 Debate Summary & Scoring:\n{final_summary}")

# Entry point
def analyze_poll_shift(pre, post):
    print("\n📈 Audience Opinion Shift Analysis:")
    for key in pre:
        shift = post[key] - pre[key]
        symbol = "📈" if shift > 0 else ("📉" if shift < 0 else "➖")
        print(f"{symbol} {key.upper()} shift: {shift} votes")

def main():
    print("🎙 Welcome to the Real-Time AI Debate Platform!")
    topic = get_debate_topic()
    user_stance = get_stance()
    duration = get_duration()

    pre_votes = collect_audience_votes(stage="before")

    ai_stance = "against" if user_stance == "for" else "for"
    debate_loop(topic, ai_stance, duration)

    post_votes = collect_audience_votes(stage="after")

    analyze_poll_shift(pre_votes, post_votes)

if __name__ == "__main__":
    main()
