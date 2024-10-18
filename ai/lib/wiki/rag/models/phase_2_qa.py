from typing import List
from pydantic import BaseModel


class Phase2QA(BaseModel):
    answer: str # the answer from the model
    document_ids: List[int] # the document IDs from which the answer is extracted
