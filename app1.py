#your python code here!
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pychord import Chord
load_dotenv()
import json
import shared_state
import platform
import subprocess
from datetime import datetime

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def summarize_for_handoff(history):
    if not history:
        return ""
    try:
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=150,
            temperature=0.3,
            system="Summarize this music theory lesson in 2-3 sentences, written in third person about the student (e.g. 'Student worked on...'). Mention topics covered and what they understood or struggled with.",
            messages=history
        )
        return response.content[0].text
    except Exception as e:
        print(f"Couldn't generate handoff summary: {e}")
        return ""


def run_chat():
    print('welcome to our app, my name is Rob ill be teaching you music theory. Hope you enjoy and learn a lot. type exit to quit btw, "help" if you need sth  and "reset" to reset your history ')

    system_message = f"""
    
You are Rob, an expert music theory tutor specializing in teaching beginners and intermediate learners through interactive conversations. Your primary responsibility is to teach music theory in a clear, patient, engaging, and encouraging way.

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

A:

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

    if os.path.exists("progress.json"):
        with open("progress.json", "r") as file:
            progress = json.load(file)
    else:
        progress = {
            "goal": shared_state.goal,
            "completed_topics": [],
            "last_summary": ""
        }

        with open("progress.json", "w") as file:
            json.dump(progress, file, indent=4)

    history = shared_state.rob_history

    dynamic_system_message = system_message + f"\n\nThe student plays {shared_state.instrument}, is at a {shared_state.level} level. Their specific goal for this session is: {shared_state.goal}"

    turn = 0
    while True:
        user_input = input(f"[Turn {turn + 1}] You: ")

        if not user_input.strip():
            continue

        if user_input.lower() == 'exit':
            summary = summarize_for_handoff(history)
            if summary:
                shared_state.shared_context = summary
            break
        if user_input.lower() == '/switch':
            summary = summarize_for_handoff(history)
            if summary:
                shared_state.shared_context = summary
            shared_state.next_agent = "2"
            break
        if user_input == "reset":
            history.clear()
            print("your history is now reset")
            continue
        if user_input == "help":
            print("type exit if you want to quit")
            print("ask anything relating to music theory and ill help you ")
            print("type reset if you want to reset your history")
            continue


        turn += 1
        history.append({'role': 'user', 'content': user_input})
        chord_fact = get_chord_info(user_input)
        scale_fact = get_scale_info(user_input)

        turn_system_message = dynamic_system_message
        if chord_fact:
            turn_system_message += f"\n\nVERIFIED CHORD FACT for this turn: {chord_fact}"
        if scale_fact:
            turn_system_message += f"\n\nVERIFIED SCALE FACT for this turn: {scale_fact}"
        if shared_state.shared_context:
            turn_system_message += f"\n\nContext from the student's other lessons: {shared_state.shared_context}\nUse this actively: if it mentions something the student struggled with, bring it up early and address it directly, rather than waiting for the student to ask."
        turn_system_message += "\n\nonly use the play chord tool if the user asks about to HEAR audio. also play a sample, or listen to a chord/scale. DO NOT call the tool for general questions, definitions, or explanations"

        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=500,
                temperature=0.7,
                system=turn_system_message,
                messages=history,
                tools=[
                    {
                        "name": "play_chord",
                        "description": "Generate a short audio file playing the given notes together as a chord or in sequence as a scale, so the student can hear it.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "notes": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of note names to play together, e.g. ['C4', 'E4', 'G4']. Octave number is optional and defaults to 4."
                                }
                            },
                            "required": ["notes"]
                        }
                    }
                ]
            )
        except Exception as e:
            print(f"Something went wrong talking to Claude: {type(e).__name__}: {e}")
            if hasattr(e, "__cause__") and e.__cause__:
                print(f"Underlying cause: {repr(e.__cause__)}")
            history.pop()
            continue

        history.append({'role': 'assistant', 'content': response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "play_chord":
                    notes = block.input.get("notes", [])
                    filename = create_chord_audio_file(notes)
                    if filename:
                        print(f"[Rob generated audio: {filename} — open it with any media player to hear it]")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Audio saved as {filename}."
                        })
                    else:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Couldn't recognize any of those notes, so no audio was generated.",
                            "is_error": True
                        })
            history.append({'role': 'user', 'content': tool_results})

            try:
                followup = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=500,
                    temperature=0.7,
                    system=turn_system_message,
                    messages=history
                )
                reply = followup.content[0].text
                history.append({'role': 'assistant', 'content': reply})
            except Exception as e:
                print(f"Something went wrong talking to Claude: {e}")
                reply = "I made the audio, but had trouble following up — check the file above!"
        else:
            reply = response.content[0].text

        print(f'Rob: {reply}')
        messages = ["Nice job my friend keep going",
                    "proud of you, amazing work",
                    "youve got this"]

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = input_tokens + output_tokens

        print(f"[Tokens used — In: {input_tokens} | Out: {output_tokens} | Total: {total_tokens}]")
        if user_input == "/summary":
            current_time = datetime.now()
            print(random.choice(messages))
            progress["last_summary"] = reply
            with open("progress.json", "w") as file:
                json.dump(progress, file, indent=4)
            shared_state.shared_context = summarize_for_handoff(history)

            with open("lesson_summary.txt", "a") as file:
                file.write(f"\nLesson Date: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(reply)


import wave
import struct
import math

NOTE_OFFSETS = {
    'C': -9, 'C#': -8, 'DB': -8, 'D': -7, 'D#': -6, 'EB': -6,
    'E': -5, 'F': -4, 'F#': -3, 'GB': -3, 'G': -2, 'G#': -1,
    'AB': -1, 'A': 0, 'A#': 1, 'BB': 1, 'B': 2
}


def note_to_freq(note):
    note = note.strip().upper()
    octave = 4
    if note and note[-1].isdigit():
        octave = int(note[-1])
        note = note[:-1]
    if note not in NOTE_OFFSETS:
        return None
    semitones = NOTE_OFFSETS[note] + (octave - 4) * 12
    return 440.0 * (2 ** (semitones / 12))



def create_chord_audio_file(notes, duration=2.0, sample_rate=44100):
    freqs = [note_to_freq(n) for n in notes]
    freqs = [f for f in freqs if f is not None]

    print("Notes:", notes)
    print("Frequencies:", freqs)

    if not freqs:
        return None

    filename = f"chord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    with wave.open(filename, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        frames = []
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            sample = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(
                freqs
            )
            value = int(sample * 32767 * 0.3)
            frames.append(struct.pack("<h", value))

        wav.writeframes(b"".join(frames))

    # Plays the audio directly on your system:
    try:
        current_os = platform.system()
        if current_os == "Windows":
            import winsound

            winsound.PlaySound(filename, winsound.SND_FILENAME)
        elif current_os == "Darwin":  # macOS
            subprocess.run(["afplay", filename])
        elif current_os == "Linux":
            subprocess.run(["aplay", filename])
    except Exception as e:
        print(f"Could not play audio automatically: {e}")

    return filename





def get_chord_info(user_input):
    for word in user_input.split():
        cleaned = word.strip(",.?!")
        try:
            chord = Chord(cleaned)
            return f"{cleaned} = {', '.join(chord.components())}"
        except ValueError:
            continue
    return None


major_scales = {
    "C": ["C", "D", "E", "F", "G", "A", "B"],
    "D": ["D", "E", "F#", "G", "A", "B", "C#"],
    "G": ["G", "A", "B", "C", "D", "E", "F#"],
    "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
}


def get_scale_info(user_input):
    words = user_input.replace(",", "").split()
    for i in range(len(words)):
        if words[i].lower() == "major" and i > 0:
            root = words[i - 1]
            if root in major_scales:
                notes = ", ".join(major_scales[root])
                return f"{root} major scale = {notes}"
    return None
