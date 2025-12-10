from typing import Any, Dict
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


print("✅ ADK components imported successfully.")

load_dotenv()

APP_NAME = "default"
USER_ID = "default"
MODEL_NAME = "gemini-2.5-flash"

# Retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -----------------------------
# SESSION RUNNER
# -----------------------------
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    print(f"\n ### Session: {session_name}")

    app_name = runner_instance.app_name

    # Создаём или получаем сессию
    try:
        session = await session_service.create_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=session_name,
        )
    except:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=session_name,
        )

    if user_queries:
        if isinstance(user_queries, str):
            user_queries = [user_queries]

        for query in user_queries:
            print(f"\nUser > {query}")

            query = types.Content(
                role="user",
                parts=[types.Part(text=query)],
            )

            async for event in runner_instance.run_async(
                user_id=USER_ID,
                session_id=session.id,
                new_message=query,
            ):
                if event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text and text != "None":
                        print(f"{MODEL_NAME} > {text}")
    else:
        print("No queries!")


print("✅ Helper functions defined.")

# -----------------------------
# LLM AGENT
# -----------------------------
chatbot_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    name="text_chat_bot",
    description="A text chatbot with compaction memory",
)

# -----------------------------
# ✅ COMPACTION ENABLED APP
# ✅ ONLY WITH InMemorySessionService
# -----------------------------
session_service = InMemorySessionService()

research_app_compacting = App(
    name="research_app_compacting",
    root_agent=chatbot_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # ✅ каждые 3 сообщения
        overlap_size=1,        # ✅ оставить 1 прошлый turn
    ),
)

research_runner_compacting = Runner(
    app=research_app_compacting,
    session_service=session_service,
)

print("✅ Research App upgraded with Events Compaction!")

# -----------------------------
# ✅ MAIN FLOW — 4 TURNS
# -----------------------------
async def main():
    # Turn 1
    await run_session(
        research_runner_compacting,
        "What is the latest news about AI in healthcare?",
        "compaction_demo",
    )

    # Turn 2
    await run_session(
        research_runner_compacting,
        "Are there any new developments in drug discovery?",
        "compaction_demo",
    )

    # ✅ Turn 3 — AFTER THIS TURN COMPACTION TRIGGERS
    await run_session(
        research_runner_compacting,
        "Tell me more about the second development you found.",
        "compaction_demo",
    )

    # Turn 4 — уже после compaction
    await run_session(
        research_runner_compacting,
        "Who are the main companies involved in that?",
        "compaction_demo",
    )





    # Get the final session state
    final_session = await session_service.get_session(
        app_name=research_runner_compacting.app_name,
        user_id=USER_ID,
        session_id="compaction_demo",
    )

    print("--- Searching for Compaction Summary Event ---")
    found_summary = False
    for event in final_session.events:
        # Compaction events have a 'compaction' attribute
        if event.actions and event.actions.compaction:
            print("\n✅ SUCCESS! Found the Compaction Event:")
            print(f"  Author: {event.author}")
            print(f"\n Compacted information: {event}")
            found_summary = True
            break

    if not found_summary:
        print(
            "\n❌ No compaction event found. Try increasing the number of turns in the demo."
        )

    # ✅ One single asyncio loop
asyncio.run(main())