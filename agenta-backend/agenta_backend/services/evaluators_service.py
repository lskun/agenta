import re
import httpx
from typing import Any, Dict, Tuple

from agenta_backend.services.db_manager import Result

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


def auto_exact_match(
    variant_output: str, correct_answer: str, settings_values: Dict[str, Any]
) -> Result:
    exact_match = True if variant_output == correct_answer else False
    result = Result(type="bool", value=exact_match)
    return result


def auto_similarity_match(
    variant_output: str, correct_answer: str, settings_values: Dict[str, Any]
) -> Result:
    set1 = set(variant_output.split())
    set2 = set(correct_answer.split())
    intersect = set1.intersection(set2)
    union = set1.union(set2)

    similarity = len(intersect) / len(union)

    is_similar = True if similarity > settings_values["similarity_threshold"] else False
    result = Result(type="bool", value=is_similar)
    return result


def auto_regex_test(
    variant_output: str, correct_answer: str, settings_values: Dict[str, Any]
) -> Result:
    re_pattern = re.compile(settings_values["regex_pattern"], re.IGNORECASE)
    result = (
        bool(re_pattern.search(variant_output)) == settings_values["regex_should_match"]
    )
    return Result(type="bool", value=result)


def auto_webhook_test(
    variant_output: str, correct_answer: str, settings_values: Dict[str, Any]
) -> Result:
    try:
        with httpx.Client() as client:
            response = client.post(
                url=settings_values["webhook_url"], json=settings_values["webhook_body"]
            )
            response.raise_for_status()
            response_data = response.json()
            score = response_data.get("score", None)
            if not score:
                raise httpx.HTTPError("Webhook did not return a score")
            if score < 0 or score > 1:
                raise httpx.HTTPError(
                    "Webhook returned an invalid score. Score must be between 0 and 1"
                )
            return Result(type="number", value=score)
    except httpx.HTTPError as e:
        print(f"An HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def auto_ai_critique(
    llm_app_prompt_template: str,
    llm_app_inputs: list,
    correct_answer: str,
    app_variant_output: str,
    evaluation_prompt_template: str,
    open_ai_key: str,
    temperature: float = 0.9,
) -> str:
    """Evaluate a response using an AI critique based on provided
     - An evaluation prompt,
     - An LLM App prompt,
     - An LLM App output,
     - a correct answer.

    Args:
        llm_app_prompt_template (str): the prompt template of the llm app variant
        llm_app_inputs (list): parameters
        correct_answer (str): correct answer
        app_variant_output (str): the output of an ll app variant with given parameters
        evaluation_prompt_template (str): evaluation prompt set by an agenta user in the ai evaluation view

    Returns:
        str: returns an evaluation
    """
    llm = OpenAI(openai_api_key=open_ai_key, temperature=temperature)

    input_variables = []

    # List of default variables
    default_vars = [
        "app_variant_output",
        "llm_app_prompt_template",
        "correct_answer",
    ]

    # Check default variables
    for var in default_vars:
        if "{%s}" % var in evaluation_prompt_template:
            input_variables.append(var)

    # Iterate over llm_app_inputs and check if the variable name exists in the evaluation_prompt_template
    for input_item in llm_app_inputs:
        if "{%s}" % input_item["input_name"] in evaluation_prompt_template:
            input_variables.append(input_item["input_name"])

    chain_run_args = {
        "llm_app_prompt_template": llm_app_prompt_template,
        "correct_answer": correct_answer,
        "app_variant_output": app_variant_output,
    }

    for input_item in llm_app_inputs:
        chain_run_args[input_item["input_name"]] = input_item["input_value"]

    prompt = PromptTemplate(
        input_variables=input_variables, template=evaluation_prompt_template
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    output = chain.run(**chain_run_args)
    return output.strip()


def evaluate(
    evaluator_name: str,
    correct_answer: str,
    variant_output: str,
    settings_values: Dict[str, Any],
    *additional_args: Tuple[Any],
    **additional_kwargs: Dict[str, Any],
) -> Result:
    try:
        evaluation_function = globals()[evaluator_name]
        return evaluation_function(
            correct_answer,
            variant_output,
            settings_values,
            *additional_args,
            **additional_kwargs,
        )
    except KeyError:
        raise ValueError(f"Evaluation method '{evaluator_name}' not found.")
