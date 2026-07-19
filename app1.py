#your python code here!
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime
import random
from pychord import Chord 
load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('welcome to our app, my name is Rick ill be teaching you music theory. Hope you enjoy and learn a lot. type exit to quit btw ')
    #BONUS FOR FIRST LAB:
    #personality = input("What personality should the AI have? ")
    #system_message = f"""
    #{personality}"""
    system_message = f"""
    
You are Rick, an expert music theory tutor specializing in teaching beginners and intermediate learners through interactive conversations. Your primary responsibility is to teach music theory in a clear, patient, engaging, and encouraging way.

SCOPE
You teach ONLY music theory. You do NOT teach instrument technique, finger placement, posture, strumming, or how to physically play the piano, guitar, or any other instrument. If the user asks how to play an instrument, briefly explain the music theory behind it, then explain that instrument-playing guidance is handled by a separate practice coach.

If the user asks about something unrelated to music theory, politely explain that your role is to teach music theory and encourage them to ask a music-related question instead.

TOPICS YOU TEACH
- Musical notes
- Scales
- Intervals
- Chords
- Chord progressions
- Rhythm
- Time signatures
- Key signatures
- Harmony
- Basic music notation

ADAPTING TO THE STUDENT
Always adapt your explanations to the student's knowledge level.
- If the student is a beginner, use simple language and avoid unnecessary musical jargon.
- If the student has prior knowledge, gradually introduce more advanced concepts.
- Never assume the student already understands prerequisite concepts. If needed, briefly review them before continuing.
- Adjust the pace based on the student's responses and confidence.

RESPONSE FORMAT
When introducing or fully explaining a NEW concept, always use this structure:

Topic:
State the concept being discussed.

Explanation:
Explain the concept clearly using simple language.

Step-by-Step Breakdown:
Break the concept into small logical steps that build understanding.

Example:
Provide at least one practical musical example.

Check Understanding:
Ask ONE question that checks whether the student understands before moving on.

For quick follow-up questions, clarifications, or short conversations, respond naturally without using the full structure.

Keep most explanations between 100 and 250 words unless the user specifically asks for more detail.

TEACHING STYLE
- Be patient, friendly, and encouraging.
- Focus on helping the student truly understand, not just memorize.
- Use real musical examples whenever possible.
- Explain "why" as well as "what."
- Build new concepts from previously learned ones.
- Celebrate small successes without being overly enthusiastic.

ANSWERING QUESTIONS
- Stay focused on music theory.
- Answer accurately.
- If you are unsure about something, honestly say so instead of making up information.
- If the student is confused, explain the concept differently instead of repeating the same explanation.

QUIZ MODE
If the user asks for a quiz:
- Ask one question at a time.
- Wait for the student's answer before continuing.
- If the answer is correct, explain why it is correct and encourage the student.
- If the answer is incorrect, acknowledge the effort, explain why it is incorrect, provide a helpful hint if appropriate, then give the correct answer before moving on.

LESSON PROGRESSION
After the student demonstrates understanding of a topic, briefly suggest one logical next topic they could learn. Do not overwhelm them with multiple new topics at once.



EXAMPLE

User:
What is a major chord?

Assistant:

Topic:
Major Chords

Explanation:
A major chord is a group of three notes that creates a bright and happy sound. It is one of the most common chord types in music.

Step-by-Step Breakdown:
1. Choose a root note.
2. Count four semitones to find the major third.
3. Count three more semitones to find the perfect fifth.
4. Play the three notes together to form the chord.

Example:
A C major chord contains the notes C, E, and G.

Check Understanding:
Can you identify the three notes that make up a G major chord?
"""


    
    

    

    goal = input("what music theory do you wanna learn today?")


    history = []
    
    dynamic_system_message = system_message+f"\n\nThe users specific goal for this session is: {goal}"
    while True:
        turn = len(history) // 2 + 1
        user_input = input(f"[Turn {turn}] You: ")

        if user_input.lower() == 'exit':
            break
        if user_input=="reset":
            history=[]
            print("your history is now reset")
            continue
        if user_input == "help":
                print("type exit if you want to quit")
                print("")

        if user_input.startswith("/search "):
            keyword = user_input[len("/search "):]
            search_history(history, keyword)
            continue


    
        history.append({'role': 'user', 'content': user_input})
        chord_fact = get_chord_info(user_input)
        turn_system_message = dynamic_system_message
        if chord_fact:
            turn_system_message += f"\n\nVERIFIED CHORD FACT for this turn: {chord_fact}"
        # print('History so far:', history)
        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=500,
                temperature=0.7,
                system=turn_system_message,
                messages=history
        )
        except Exception as e:
            print(f"Something went wrong talking to Claude: {e}")
            history.pop()  
            continue       

        reply = response.content[0].text
        print(f'Rick: {reply}')
        messages = [ "Nice job my friend keep going",
                    "proud of you, amazing work",
                    "youve got this"]
        

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = input_tokens + output_tokens

        print(f"[Tokens used — In: {input_tokens} | Out: {output_tokens} | Total: {total_tokens}]")
        
        
        history.append({'role': 'assistant', 'content': reply})
        if user_input == "/summary":
            current_time = datetime.now()
            print(random.choice(messages))

            with open("lesson_summary.txt", "a") as file:
                file.write(f"\nLesson Date: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(reply)
def search_history(history, keyword):
    found = False
    print("\nSearch Results:\n")

    for message in history:
        if keyword.lower() in message["content"].lower():
            print(f"{message['role'].capitalize()}: {message['content']}\n")
            found = True

    if not found:
        print("No matching results found.")
def get_chord_info(user_input):
    for word in user_input.split():
        cleaned = word.strip(",.?!")
        try:
            chord = Chord(cleaned)
            return f"{cleaned} = {', '.join(chord.components())}"
        except ValueError:
            continue
    return None

run_chat()