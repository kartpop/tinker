from typing import List
from pydantic import BaseModel


class P2QA(BaseModel):
    answer: str
    document_ids: List[int]
