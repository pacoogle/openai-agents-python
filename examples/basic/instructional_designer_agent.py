from __future__ import annotations

import asyncio
import json
from dotenv import load_dotenv
from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace
load_dotenv()

# Agente per la raccolta e validazione delle informazioni del corso
course_information_manager = Agent(
    name="course_generator",
    instructions=(
        "You are an intelligent agent responsible for generating a course for Gamindo Builder based on user-provided information. "
        "Your task is to collect and validate the following details from the user:\n"
        "- Duration (in minutes)\n"
        "- Difficulty level (easy, medium, or hard)\n"
        "- Language (choose one from the languages supported by GPT-4)\n"
        "- Tone of voice (funny, serious, or with emojis)\n"
        "- Theme (user's choice)\n"
        "- Challenge composition (only quizzes, only true-false, or mixed)\n\n"
        "IMPORTANT: If any of these details are missing from the user's input, do not assume default values. Instead, explicitly ask the user to provide the missing information. "
        "Only output the final JSON when all required details have been provided. Your output must strictly follow this JSON format:\n"
        "{\"duration\": <number>, "
        "\"difficulty\": \"<easy/medium/hard>\", "
        "\"language\": \"<language>\", "
        "\"tone_of_voice\": \"<funny/serious/with emojis>\", "
        "\"theme\": \"<theme>\", "
        "\"challenge_composition\": \"<only quizzes/only true-false/mixed>\"}\n\n"
        "If additional feedback is provided, incorporate it to refine and improve the course. "
        "Ensure complete adherence to this structure and maintain clarity and consistency in your output."
    ),
)

# Agente per generare i contenuti del corso in base alle informazioni raccolte
course_content_generator = Agent(
    name="course_content_generator",
    instructions=(
        "You are an intelligent agent responsible for generating course content for Gamindo Builder. "
        "Based on the provided course information, your task is to generate the course challenges in the correct JSON format. "
        "Follow these rules:\n\n"
        "- If the 'challenge_composition' field is 'only quizzes', output a JSON array of quiz challenges using the following format:\n"
        "[{\"question\": \"domanda\", \"answers\": [\"risposta 1\", \"risposta 2\"]}]\n\n"
        "- If the 'challenge_composition' field is 'only true-false', output a JSON array of true/false challenges using the following format:\n"
        "[{\"question\": \"domanda\", \"answers\": [\"vero\", \"falso\"]}]\n\n"
        "- If the 'challenge_composition' field is 'mixed', output a JSON array that combines both types of challenges.\n\n"
        "Your output must be valid JSON following exactly the structure corresponding to the 'challenge_composition' provided in the course information."
    ),
)


async def main() -> None:
    # Richiesta iniziale di input all'utente
    msg = input("How can I help you? Do you want to create a 'training path' or a 'random path'? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]
    final_course_info = None

    # Loop per la raccolta delle informazioni complete del corso
    with trace("Course Information Collection"):
        while True:
            course_result = await Runner.run(course_information_manager, input_items)
            output_str = ItemHelpers.text_message_outputs(course_result.new_items)
            print("\nAgent output:\n" + output_str)

            try:
                course_info = json.loads(output_str)
            except json.JSONDecodeError:
                feedback = "The output is not valid JSON. Please provide a valid JSON following the specified format."
                print(feedback)
                user_feedback = input("Enter corrected information: ")
                input_items.append({"content": f"Feedback: {user_feedback}", "role": "user"})
                continue

            # Verifica che ogni campo richiesto sia presente e non vuoto
            required_keys = ["duration", "difficulty", "language", "tone_of_voice", "theme", "challenge_composition"]
            missing_keys = [key for key in required_keys if key not in course_info or not course_info[key]]
            if missing_keys:
                feedback = (
                    f"The following fields are missing or empty: {', '.join(missing_keys)}. "
                    "Please provide the missing details."
                )
                print(feedback)
                user_feedback = input("Enter missing information: ")
                input_items.append({"content": f"Feedback: {user_feedback}", "role": "user"})
                continue

            final_course_info = course_info
            break

    print("\nFinal Course Information Recap:")
    print(json.dumps(final_course_info, indent=4))

    # Generazione dei contenuti del corso basata sulle informazioni raccolte
    course_info_str = json.dumps(final_course_info)
    content_input_items: list[TResponseInputItem] = [{"content": course_info_str, "role": "user"}]
    with trace("Course Content Generation"):
        content_result = await Runner.run(course_content_generator, content_input_items)
        content_output = ItemHelpers.text_message_outputs(content_result.new_items)
        print("\nGenerated Course Content:")
        print(content_output)


if __name__ == "__main__":
    asyncio.run(main())
