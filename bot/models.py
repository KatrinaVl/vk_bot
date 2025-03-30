from pydantic import BaseModel
from typing import Dict

class Variant(BaseModel):
    title: str
    votes: int = 0

class Poll(BaseModel):
    id: str
    text: str
    variants: Dict[str, int]
    author: str
    is_open: bool = True

class Vote(BaseModel):
    poll_id: str
    variant: str
    user: str