from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain, TransformChain
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

import agenta as ag

ag.init(project_id="0192813f-60d5-7a65-8a75-6dda36b79267",
        host="https://cloud.beta.agenta.ai",
        api_key="NYWy4We0.17ce0e85db4840a39ca9ee7b00e8817b22b60d7e152407a5a4cc98c5284f2e0e",
        app_id="0192b552-ad65-7c61-a8dc-fedf3608b7a5")

LangchainInstrumentor().instrument()


def langchain_app():
    chat = ChatOpenAI(temperature=0)

    transform = TransformChain(
        input_variables=["subject"],
        output_variables=["prompt"],
        transform=lambda subject: {"prompt": f"Tell me a joke about {subject}."},
    )

    first_prompt_messages = [
        SystemMessage(content="You are a funny sarcastic nerd."),
        HumanMessage(content="{prompt}"),
    ]
    first_prompt_template = ChatPromptTemplate.from_messages(first_prompt_messages)
    first_chain = LLMChain(llm=chat, prompt=first_prompt_template, output_key="joke")

    second_prompt_messages = [
        SystemMessage(content="You are an Elf."),
        HumanMessagePromptTemplate.from_template(
            "Translate the joke below into Sindarin language:\n {joke}"
        ),
    ]
    second_prompt_template = ChatPromptTemplate.from_messages(second_prompt_messages)
    second_chain = LLMChain(llm=chat, prompt=second_prompt_template)

    workflow = SequentialChain(
        chains=[transform, first_chain, second_chain], input_variables=["subject"]
    )
    print(workflow({"subject": "OpenTelemetry"}))


langchain_app()