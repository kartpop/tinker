from typing import List
from pydantic import BaseModel


class Phase1QA(BaseModel):
    answer: str  # the answer from the model
    need_more_context: bool  # whether more context is needed
    reasoning: str  # the reasoning behind the answer
    document_ids: List[int]  # the document IDs from which the answer is extracted
