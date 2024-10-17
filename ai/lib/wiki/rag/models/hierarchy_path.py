from typing import List
from pydantic import BaseModel


class HierarchyPath(BaseModel):
    path: List[str]
    reasoning: str


class HierarchyPathData(BaseModel):
    paths: List[HierarchyPath]
