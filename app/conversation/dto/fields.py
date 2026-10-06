"""Reusable validated field types for conversation DTOs."""

from typing import Annotated

from pydantic import StringConstraints


# Fits comfortably in a MySQL TEXT column (64 KB) even at 4 bytes/char.
MESSAGE_MAX_LENGTH = 10_000

ConversationTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]

MessageContent = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=MESSAGE_MAX_LENGTH,
    ),
]
