"""Shared request parameters."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Path, Query


@dataclass(frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationParams = Annotated[Pagination, Depends(get_pagination)]

ConversationId = Annotated[int, Path(gt=0)]
