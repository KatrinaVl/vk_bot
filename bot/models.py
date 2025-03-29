from pydantic import BaseModel
from typing import List, Dict, Optional

class Poll(BaseModel):
    id: str
    text: str
    variants: Dict[str, Variant]
    author: str
    is_open: bool = True

class Variant(BaseModel):
    title: str
    votes: int = 0

class CreatePoll(BaseModel):
    text: str
    variants: List[str]
    author: str

class Vote(BaseModel):
    variant_id: str
    author: str
    user: str