# app/agent_wrapper.py
import os
from dotenv import load_dotenv
import asyncio

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Gemini/OpenAI client
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

# Tools
@function_tool
def about_me_tool(query: str) -> str:
    q = query.lower()
    if "who made you" in q or "who is your creator" in q:
        return (
            "Mujhe Fatima Farooq Khuwaja ne banaya hai. "
            "Woh ek talented Full Stack Developer, Python Expert aur Agentic AI Engineer hain 😊"
        )
    elif "who is fatima" in q or "tell me about fatima" in q:
        return (
            "Fatima Farooq Khuwaja ek passionate Full Stack Engineer hain jo currently 2nd year (Intermediate) ki student hain. "
            "Woh Next.js aur Python dono me expert hain. "
            "Fatima GIAIC ki student hain aur abhi Quarter 3 me Agentic AI parh rahi hain. "
            "Unhon ne 100+ websites develop ki hain, jisme eCommerce, banking, QCommerce, music gallery, portfolio, blog, fullstack form, committee apps waghera shamil hain. "
            "Python me unke projects me password strength meter, personal library manager, password generator, unit converter, money generator, calculator aur random joke generator jaise apps shamil hain. "
            "Unka aim AI aur software engineering me excellence hasil karna hai. 🚀"
        )
    else:
        return (
            "Main ek AI chatbot hoon jo Fatima Farooq Khuwaja ne banaya hai. "
            "Woh ek Full Stack Developer aur Python expert hain. "
            "Agar aap Fatima ke baare me detail se jan'na chahte hain to poochh sakte hain. 😊"
        )

# Coordinator Agent
coordinator_agent = Agent(
    name="coordinator",
    instructions="Respond based on user input; use about_me_tool for creator/Fatima questions.",
    tools=[about_me_tool],
)

# Async function to call agent
async def get_agent_response(prompt: str) -> str:
    result = await Runner.run(coordinator_agent, input=prompt, run_config=config)
    return getattr(result, "final_output", str(result)).strip()
