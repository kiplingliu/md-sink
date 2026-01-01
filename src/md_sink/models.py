from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Rating(Enum):
    FAIL = 1
    PASS = 2

class Review(BaseModel):
    time: datetime
    rating: Rating

class Metadata(BaseModel):
    reviews: list[Review] = []
    
@dataclass
class Card:
    front: str
    metadata: Metadata
    back: list[str]
    front_extra: list[str]

@dataclass
class Deck:
    heading_level: int
    cards: list[Card]

@dataclass
class NonDeck:
    lines: list[str]
