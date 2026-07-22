from app1 import run_chat as mtheory_chat
from app2 import run_chat as mteacher_chat
import shared_state


def setup():
    shared_state.instrument = input(
        "What instrument do you play or dou want to learn to play? (Guitar / Piano) >> "
    ).strip().lower()

    while shared_state.instrument not in ["guitar", "piano"]:
        shared_state.instrument = input(
            "Enter a valid instrument: (Guitar / Piano) >> "
        ).strip().lower()

    shared_state.goal = input(
        "What is your goal for this lesson, what do you want to learn about?\n>> "
    ).strip()

    shared_state.level = input(
        "What playing level are you at? (beginner / intermediate / pro) >> "
    ).strip().lower()

    while shared_state.level not in ["beginner", "intermediate", "pro"]:
        shared_state.level = input(
            "Enter a valid level: (beginner / intermediate / pro) >> "
        ).strip().lower()


setup()


while True:

    agent = input("""
Choose your teacher:

1 - Music Theory Teacher (Rob)
2 - Practical Music Teacher (Rick)

Type exit to quit the app or switch, to switch between agents.

>>
""").strip().lower()


    if agent == "1":
        mtheory_chat()


    elif agent == "2":
        mteacher_chat()


    elif agent == "exit":
        print("Goodbye! Keep practicing 🎵")
        break


    else:
        print("Invalid option, try again.")

            
