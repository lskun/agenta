# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class EvaluationType(str, enum.Enum):
    """
    An enumeration.
    """

    AUTO_EXACT_MATCH = "auto_exact_match"
    AUTO_SIMILARITY_MATCH = "auto_similarity_match"
    AUTO_REGEX_TEST = "auto_regex_test"
    AUTO_WEBHOOK_TEST = "auto_webhook_test"
    AUTO_AI_CRITIQUE = "auto_ai_critique"
    HUMAN_A_B_TESTING = "human_a_b_testing"
    HUMAN_SCORING = "human_scoring"
    CUSTOM_CODE_RUN = "custom_code_run"
    SINGLE_MODEL_TEST = "single_model_test"

    def visit(
        self,
        auto_exact_match: typing.Callable[[], T_Result],
        auto_similarity_match: typing.Callable[[], T_Result],
        auto_regex_test: typing.Callable[[], T_Result],
        auto_webhook_test: typing.Callable[[], T_Result],
        auto_ai_critique: typing.Callable[[], T_Result],
        human_a_b_testing: typing.Callable[[], T_Result],
        human_scoring: typing.Callable[[], T_Result],
        custom_code_run: typing.Callable[[], T_Result],
        single_model_test: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is EvaluationType.AUTO_EXACT_MATCH:
            return auto_exact_match()
        if self is EvaluationType.AUTO_SIMILARITY_MATCH:
            return auto_similarity_match()
        if self is EvaluationType.AUTO_REGEX_TEST:
            return auto_regex_test()
        if self is EvaluationType.AUTO_WEBHOOK_TEST:
            return auto_webhook_test()
        if self is EvaluationType.AUTO_AI_CRITIQUE:
            return auto_ai_critique()
        if self is EvaluationType.HUMAN_A_B_TESTING:
            return human_a_b_testing()
        if self is EvaluationType.HUMAN_SCORING:
            return human_scoring()
        if self is EvaluationType.CUSTOM_CODE_RUN:
            return custom_code_run()
        if self is EvaluationType.SINGLE_MODEL_TEST:
            return single_model_test()
