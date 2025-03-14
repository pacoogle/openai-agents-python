from agents import Agent, Runner
import asyncio
import os
from dotenv import load_dotenv

# Carica manualmente il .env prima di avviare gli agent
load_dotenv()

true_false_agent = Agent(
    name="Quiz expert",
    instructions="You are an expert on true|false based gameplay. Every true|false you generated must have this JSON schema {\"question\": \"Domanda\", \"answer\": [\"true\", \"false\"], \"correct_answer\": 0} true|false must have always 2 answer, 1 true and 1 false and only one correct indicated in `correct_answer` field (0 based)"
)

quiz_agent = Agent(
    name="Quiz expert",
    instructions="You are an expert on quiz based gameplay. Every quiz you generated must have this JSON schema {\"question\": \"Domanda\", \"answer\": [\"Risposta 1\", \"Risposta 2\"], \"correct_answer\": 0} Quiz must have min 2 answer and max 4 answer and only one correct indicated in `correct_answer` field (0 based)"
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the requested gameplay type between quiz and true_false. The user can ask more thant one type of gameplay in every single request!",
    handoffs=[quiz_agent, true_false_agent],
)


async def main():
    user_input = input("Come posso esserti utile?")
    result = await Runner.run(triage_agent, input=user_input)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
