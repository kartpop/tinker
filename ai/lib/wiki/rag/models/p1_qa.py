from typing import List
from pydantic import BaseModel


class P1QA(BaseModel):
    answer: str
    need_more_context: bool
    reasoning: str
    document_ids: List[int]
