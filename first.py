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


# response = await runner.run_debug(
#     "What is Agent Development Kit from Google? What languages is the SDK available in?"
# )


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

    # print("--- Ответ Агента (маркированный список) ---")

    # if response:
    #     # 1. Берем первый (и основной) Event из списка ответов
    #     main_event = response[0]
        
    #     # 2. Проверяем, есть ли в этом Event части с контентом
    #     if hasattr(main_event.content, 'parts') and main_event.content.parts:
    #         # 3. Перебираем все части контента (Part)
    #         for part in main_event.content.parts:
    #             # 4. Выводим текст каждой части с форматированием звездочкой
    #             #    .text - это чистый текст
    #             print(f"* {part.text}")
    #     else:
    #         print("* Не удалось извлечь контент из ответа агента.")
            
    # else:
    #     print("* Агент не вернул ответа.")
        
    # print("------------------------------------------")


# await run_query()

if __name__ == "__main__":
    asyncio.run(main())