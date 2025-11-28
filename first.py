import os
import asyncio
from dotenv import load_dotenv 

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types


load_dotenv() 


print("✅ ADK components imported successfully.")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

print("✅ Root Agent defined.")


runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")

async def main():
    print("start agent")
    response = await runner.run_debug( "What is Agent Development Kit from Google? What languages is the SDK available in?")
    print("response")
    print(response)
    print("-----------------------------------------")
    print("--- Ответ Агента (форматированный) ---")
    if response and response[0].content.parts:
        # Извлекаем текст из первого (и основного) элемента ответа
        agent_text = response[0].content.parts[0].text
        print(agent_text)
    else:
        print("Не удалось получить текстовый ответ.")
        
    print("*************************************************************************************************************************")



if __name__ == "__main__":
    asyncio.run(main())
