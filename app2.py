from operator import add
import os
from anthropic import Anthropic
from dotenv import load_dotenv


import json

with open("musical.json", "r") as file:
    data = json.load(file)

load_dotenv()
user_input = "hi"
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    user_input = ""
    def user_account():
        user_found = False
        while not user_found:
            user_profile = input("sign in / sign up \n>> ")
            if user_profile.lower() == 'sign in':
                num_tries = 0
                
                while True:
                    username = input("Enter your username: \n>> ").strip().lower()
                    if username.strip().lower() in ["back", "sign up"]:
                        print("Sign up")
                        user_profile = "sign up"
                        break
                        
                    for user in data:
                        
                        username_dict = user.get("username", {})
                        
                        if username in username_dict:
                            user_input = username_dict[username].get("goal")
                            user_found = True
                            break
                            
                    
                    if not user_found:
                        print("User not found: TRY AGAIN")
                        num_tries += 1
                        if num_tries > 3:
                            print("Too many attempts")
                            user_input = input("Guest mode\n----------\nWhat do You want to learn today? \n>> ")
                            break  
                    else:
                        break           
                    
    

            elif user_profile.lower() == "sign up":           
                new_profile = input("Do you want to create a new profile? (yes/no) \n>> ").strip()
                if new_profile.lower().strip() in ["yes", "yeah", "ye"]:
                    #NEW USERNAME
                    username = input("Enter a new username: \n>> ").strip()
                    
                    #INSTRUMENT
                    instrument = input("What instrument do you play? (Guitar / Piano) >>").strip().lower()
                    while instrument != "guitar" and instrument != "piano":
                        instrument = input("Enter a valid instrument: (Guitar / Piano) >>").strip().lower()

                    #GOAL
                    goal = input("What is your goal for this lesson? \n>> ").strip()
                    


                    level = input("What playing level are you at? (beginner / intermediate / pro) >>").strip().lower()

                    while level.lower().strip() not in["beginner", "intermediate", "pro"]:
                        level = input("Enter a valid level: (beginner / intermediate / pro) >>").strip().lower()   

                    data.append({
                        "username": {
                            username: {
                                "instrument": instrument,
                                "goal": goal,
                                "level": level
                        }
                    }
                })
                    with open("musical.json", "w") as file:
                        json.dump(data, file, indent=4)
                    user_input = goal
                    break
                else:
                    print("Guest mode activated. Starting with default lesson.")
                    user_input = input("What do You want to learn today? \n>> ")
                    break
            
            else:
                print("Please enter an avilable option\n>> ")
    user_account()
    print('You: (type exit to quit) \nTYPE /HELP FOR A LIST OF COMMANDS')
    system_message = """
You are Rick, a professional music teacher with over 30 years of teaching experience. Your primary goal is to help students become skilled and confident musicians through clear, structured, and accurate instruction. You teach piano as your primary instrument and guitar as a secondary instrument. You specialize in instrument technique, rhythm, practice methods, and helping students improve their playing.

Always teach as a real instructor, not as a general chatbot. Be friendly, patient, encouraging, and professional while maintaining high teaching standards. Never guess or invent information. If you are uncertain about something, say so rather than providing incorrect information.

Adapt every response to the student's current ability, experience, and goals. Explain concepts step by step, using simple language for beginners and more advanced explanations for experienced students.

Whenever appropriate, organize lessons using a structure similar to:

1. Lesson Goal
2. Explanation
3. Technique or Demonstration
4. Practice Exercise(s)
5. Common Mistakes
6. Practice Tips
7. Next Steps

When teaching instruments, focus on proper technique, including:
- Finger positions and finger numbers
- Hand posture
- Wrist and arm movement
- Body posture
- Timing and rhythm
- Dynamics and expression
- Coordination between hands
- Efficient practice habits

Explain not only what to do, but also why it is important.

Generate useful drills, warm-ups, exercises, and practice routines that match the student's level and goals. Include specific instructions such as duration, repetitions, tempo (BPM), and progression when helpful.

Give constructive feedback that is specific, actionable, and encouraging. If a student struggles with a skill, explain it in a different way and provide exercises to improve.

Keep responses organized using headings and bullet points when appropriate. Avoid unnecessary filler or overly long responses unless the student requests detailed explanations.

If the user enters "/summary", provide a well-organized summary of the conversation, including:
- Skills learned
- Exercises completed
- Areas needing improvement
- Practice recommendations
- Next steps
"""
    
    history = []

    
    #user_goal = input("What is your goal for this lesson? if you don't have a goal, type 'none' \n>> ")
    #history.append({'role': 'user', 'content': user_goal})
    while True:

        #user_input = input(
    #f"[Turn {sum(1 for m in history if m['role'] == 'user')}]: you>> "
#)

    

        if user_input.lower() == 'exit' or user_input.lower() == '/quit':
        
            break
        

        if user_input.lower() == '/help':
            print("/help - Show available options")
            print("/lesson - Generate a lesson")
            print("/drill - Generate a drill - technique, patterns, ")
            print("/exercise - generate an exercise - finger strength, endurance, speed, etc.")
            print("/summary - Get a summary of the conversation")
            print("/progress - Check your progress")
            print("/quit - Exit the chat")
            user_input = input("Choose option\n-------------\n>> ")
            continue
            

        elif user_input.lower() == '/lesson':
            user_input = "Please generate a lesson for me."

        elif user_input.lower() == '/drill':
            user_input = "Please generate a drill for me that works towards my general goal or a specific I mentioned in this specific lesson"

        elif user_input.lower() == '/exercise':
            user_input = "Please generate an exercise for me."

        elif user_input.lower() == '/summary':
            user_input = "Please provide a summary of our conversation so far."


        elif user_input.lower() == '/progress':
            user_input = "Please provide a summary of my progress so far."
        
        elif user_input.lower() == 'exit' or user_input.lower() == '/quit':

            break
        history.append({'role': 'user', 'content': user_input})
        #print('History:', history)
        
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history
        )
        #print(response)   

        reply = response.content[0].text
        print(f'Rick: {reply}')

        history.append({'role': 'assistant', 'content': reply})
        user_input = input(f"[Turn {sum(1 for m in history if m['role'] == 'user')}]: you>> ")




run_chat()

print("hi")