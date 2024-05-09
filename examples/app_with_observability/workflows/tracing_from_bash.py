import os
import asyncio
import agenta as ag
from openai import AsyncOpenAI


os.environ["AGENTA_LLM_RUN_PLAYGROUND"] = "cloud"
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxx"

client = AsyncOpenAI()

default_prompt = (
    "Give me 10 names for a baby from this country {country} with gender {gender}!!!!"
)

ag.init(
    app_id="xxxxxxxx",
    host="https://cloud.agenta.ai",
    api_key="xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
tracing = ag.llm_tracing()
ag.config.default(
    temperature=ag.FloatParam(0.2), prompt_template=ag.TextParam(default_prompt)
)


@ag.span(type="LLM")
async def llm_call(prompt):
    chat_completion = await client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    tracing.set_span_attribute(
        "model_config", {"model": "gpt-3.5-turbo", "temperature": ag.config.temperature}
    )  # translate to {"model_config": {"model": "gpt-3.5-turbo", "temperature": 0.2}}
    tokens_usage = chat_completion.usage.dict()
    return {
        "cost": ag.calculate_token_usage("gpt-3.5-turbo", tokens_usage),
        "message": chat_completion.choices[0].message.content,
        "usage": tokens_usage,
    }


@ag.trace()
async def generate(country: str, gender: str):
    """
    Generate a baby name based on the given country and gender.

    Args:
        country (str): The country to generate the name from.
        gender (str): The gender of the baby.
    """

    prompt = ag.config.prompt_template.format(country=country, gender=gender)
    response = await llm_call(prompt=prompt)
    return response


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate(country="South Africa", gender="Male"))
