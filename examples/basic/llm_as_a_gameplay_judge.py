from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace
load_dotenv()

"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

quiz_generator = Agent(
    name="quiz_generator",
    instructions=(
        "You generate a quiz based on user_input theme! Quiz must have this JSON structure: {\"question\": \"Domanda\", \"answer\": [\"Risposta 1\", \"Risposta 2\"], \"correct_answer\": 0} Quiz must have min 2 answer and max 4 answer and only one correct indicated in `correct_answer` field (0 based)"
        "If there is any feedback provided, use it to improve the question and answers."
    ),
)


@dataclass
class EvaluationFeedback:
    score: Literal["bad", "neutral", "good"]
    feedback: str


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate a question and answers complexity quiz generated and decide if it's good enough."
        "If it's not `good` score, you provide feedback on what needs to be improved."
        "Never give it a pass on the first try."
    ),
    output_type=EvaluationFeedback,
)


async def main() -> None:
    msg = input("What kind of quiz would you like to generate and judge? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: str | None = None

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            story_outline_result = await Runner.run(
                quiz_generator,
                input_items,
            )

            input_items = story_outline_result.to_input_list()
            latest_outline = ItemHelpers.text_message_outputs(story_outline_result.new_items)

            print("Story outline generated: " + latest_outline)

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")

            if result.score == "good":
                print("Story outline is good enough, exiting.")
                break

            print("Re-running with feedback")

            input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})

    print(f"Final story outline: {latest_outline}")


if __name__ == "__main__":
    asyncio.run(main())
