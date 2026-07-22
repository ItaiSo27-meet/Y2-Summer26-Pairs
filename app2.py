from datetime import datetime
import math
import os
import random

from anthropic import Anthropic
from dotenv import load_dotenv
from music21 import interval, note
from pychord import Chord
import shared_state

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def summarize_for_handoff(history):
    if not history:
        return ""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            temperature=0.3,
            system="""
Summarize this practical music lesson in 2-3 sentences.
Write in third person about the student.

Mention:
- what instrument skills they practiced
- what they improved
- what they struggled with
- what the next teacher should know
""",
            messages=history
        )

        return response.content[0].text

    except Exception as e:
        print(f"Couldn't generate handoff summary: {e}")
        return ""

interval_list = [
    "P1",
    "m2",
    "M2",
    "m3",
    "M3",
    "P4",
    "A4",
    "d5",
    "P5",
    "m6",
    "M6",
    "m7",
    "M7",
    "P8",
]

tools = [
    {
        "name": "play_interval_all_pitches",
        "description": (
            "Starts an interval ear-training drill. Plays two-note intervals "
            "through the speakers and quizzes the student on identifying them. "
            "Call this when the student wants to practice ear training, or when "
            "you think it would help based on the lesson."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chosen_interval_str": {
                    "type": "string",
                    "description": (
                        "Starting interval, e.g. 'M3', 'P5'. Default to 'M3' if"
                        " unsure."
                    ),
                },
                "starting_octave": {
                    "type": "integer",
                    "description": "Octave to start the drill in (default 4).",
                },
            },
            "required": [],
        },
    }
]


def play_tone(frequency, duration_seconds=0.8, sample_rate=8000):
    """Plays a raw mathematical frequency directly through Linux aplay."""
    num_samples = int(duration_seconds * sample_rate)
    audio_bytes = bytearray()

    for i in range(num_samples):
        t = i / sample_rate
        # The math behind the sounds
        amplitude = math.sin(2 * math.pi * frequency * t)
        # Turning the math into a number from 0 to 255
        sample = int((amplitude + 1) * 127.5)
        # puts the math into a file
        audio_bytes.append(sample)

    with os.popen("aplay -q -r 8000 -f U8", "w") as audio_pipe:
        audio_pipe.buffer.write(audio_bytes)


def play_interval_all_pitches(chosen_interval_str="M3", starting_octave=4):
    """Loops through all 12 pitches of an octave and plays the music21 interval."""
    print("""
Interval Guide:
Perfect Consonance: P1, P4, P5, P8
Imperfect Consonance: m3, M3, m6, M6
Soft Dissonance: M2, m7, A4, d5
Sharp Dissonance: m2, M7
""")

    base_midi_c = random.randint(36, 72)
    semitone_offset = 0
    interval_guess = ""

    while interval_guess.lower().strip() not in [
        "exit",
        "exi",
        "eit",
        "egsit",
        "ecsit",
        "quit",
        "leave",
    ]:
        semitone_offset += 1
        one_to_11 = random.randint(1, 11)

        current_midi_number = base_midi_c + one_to_11

        note1 = note.Note()
        note1.pitch.midi = current_midi_number

        chosen_interval_str = random.choice(interval_list)
        note2 = interval.Interval(chosen_interval_str).transposeNote(note1)

        freq1 = note1.pitch.frequency
        freq2 = note2.pitch.frequency

        interval_order = random.randint(1, 2)

        if interval_order == 1:
            print("Acending")
            print(f"Interval {semitone_offset + 1}: Note 1 -> Note2")
            play_tone(freq1)
            play_tone(freq2)
        else:
            print("Decending")
            print(f"Interval {semitone_offset + 1}: Note 2 -> Note 1")
            play_tone(freq2)
            play_tone(freq1)

        print(
            "Guess the interval! >>Type: 'again' to repeat \nType 'exit' to"
            " leave"
        )
        interval_guess = input("Enter guess>>\n")

        while interval_guess.lower().strip() == "again":
            if interval_order == 1:
                play_tone(freq1)
                play_tone(freq2)
                interval_guess = input("Enter guess>>\n")
            else:
                play_tone(freq2)
                play_tone(freq1)
                interval_guess = input("Enter guess>>\n")

        if interval_guess.lower().strip() in [
            "exit",
            "exi",
            "eit",
            "egsit",
            "ecsit",
            "quit",
            "leave",
        ]:
            break

        if interval_guess == chosen_interval_str:
            print("correct! moving on to The next interval >> \n\n")
        else:
            print(
                f"Wrong\nInterval: {chosen_interval_str}  -->>>> "
                f" {note1.nameWithOctave} -> {note2.nameWithOctave}\n--------"
            )

        os.system("sleep 0.3")


def run_chat():
    print("You: (type exit to quit) \nTYPE /HELP FOR A LIST OF COMMANDS")

    system_message = f"""
You are Rick, a professional music teacher with over 30 years of teaching experience. Your primary goal is to help students become skilled and confident musicians through clear, structured, and accurate instruction. You teach piano as your primary instrument and guitar as a secondary instrument. You specialize in instrument technique, rhythm, practice methods, and helping students improve their playing.

Always teach as a real instructor, not as a general chatbot. Be friendly, patient, encouraging, and professional while maintaining high teaching standards. Never guess or invent information. If you are uncertain about something, say so rather than providing incorrect information.

Adapt every response to the student's current ability, experience, and goals. Explain concepts step by step, using simple language for beginners and more advanced explanations for experienced students. If the user wants to not put in information about himself and his playing level, just keep the conversation going, and stop asking him for it.

When the user wants to practice ear training or identify musical intervals, call the `play_interval_all_pitches` tool.

Whenever appropriate, organize lessons using a structure similar to:

1. Lesson Goal
2. Explanation
3. Technique or Demonstration
4. Practice Exercise(s)
5. Common Mistakes
6. Practice Tips
7. Next Steps

The student's information:
Instrument: {shared_state.instrument}
Level: {shared_state.level}
Goal: {shared_state.goal}

Previous lesson context from Rob (music theory teacher):
{shared_state.shared_context}

Use this context actively:
- If Rob mentioned the student struggled with something, help them improve it.
- If Rob taught a theory concept, connect it to practical playing.
- Do not repeat the entire theory lesson; show how to apply it on the instrument.

Keep responses organized using headings and bullet points when appropriate.
"""

    history = shared_state.rick_history

    while True:
        user_input = input("you>> ")
        while user_input.strip() == "":
            print("Please enter a valid answer")
            user_input = input("you>> ")

        if user_input.lower() in ["exit", "/quit"]:
            break


        if user_input.lower() == "/switch":
            summary = summarize_for_handoff(history)

            if summary:
                shared_state.shared_context = summary

                shared_state.next_agent = "1"
            break

        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history,
            tools=tools,
            tool_choice={"type": "auto"},
        )

        while response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if (
                    block.type == "tool_use"
                    and block.name == "play_interval_all_pitches"
                ):
                    play_interval_all_pitches(**block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": (
                            "Ear training drill finished successfully by user."
                        ),
                    })

            history.append({"role": "user", "content": tool_results})

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history,
                tools=tools,
                tool_choice={"type": "auto"},
            )

        reply_text = "".join(
            [
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            ]
        )

        print(f"Rick: {reply_text}")
        history.append({"role": "assistant", "content": response.content})







  









