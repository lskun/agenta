# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class Status(str, enum.Enum):
    """
    An enumeration.
    """

    INITIATED = "INITIATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def visit(
        self,
        initiated: typing.Callable[[], T_Result],
        completed: typing.Callable[[], T_Result],
        failed: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is Status.INITIATED:
            return initiated()
        if self is Status.COMPLETED:
            return completed()
        if self is Status.FAILED:
            return failed()
