import re
import json
from md_sink.models import Card, Deck, NonDeck, Metadata

class ParserError(Exception):
    pass

# lines are tokens
class Parser:
    DECK_PATTERN = "^(#+) deck"

    def __init__(self, lines: list[str]):
        self._lines = lines
        self._current = 0
    
    def parse(self) -> list[Deck | NonDeck]:
        sections = []
        while not self._is_at_end():
            sections.append(self._section())
        return sections

    # precondition: we will always have at least 1 line left to parse
    # therefore, NonDeck is >=1 lines not matching the deck pattern
    def _section(self) -> Deck | NonDeck:
        if (deck := self._deck()):
            return deck
        else:
            res = []
            while not self._is_at_end() and not self._check(self.DECK_PATTERN):
                res.append(self._advance())
            return NonDeck(res)

    # Deck is a deck heading plus >=0 cards
    def _deck(self) -> Deck | None:
        if self._is_at_end() or not (m := self._match(self.DECK_PATTERN)):
            return None
        
        self._consume_newlines()

        res = []
        deck_heading_level = len(m.group(1))
        card_heading_level = deck_heading_level + 1
        while not self._is_at_end():
            if (card := self._card(card_heading_level)):
                res.append(card)
            else:
                break

        return Deck(deck_heading_level, res)
    
    # Card is:
    # 1. card heading (containing the front of the card)
    # 2. optional extra front data
    # 3. optional metadata
    # 4. back, defined as >=0 lines not matching card or deck pattern
    #
    # in the absence of optional metadata, we assume that extra front
    # data doesn't exist
    #
    # grammar:
    # Card = CardHeading Body
    # Body = Content [Metadata Content]
    def _card(self, heading_level: int) -> Card | None:
        card_pattern = "^" + "#" * heading_level + " (.*)"
        if self._is_at_end() or not (m := self._match(card_pattern)):
            return None

        front = m.group(1)
        self._consume_newlines()

        end_pattern = "^#{1," + str(heading_level) + "}"
        buffer = [] # content block before either metadata or end
        metadata = None
        while (not self._is_at_end() and
               not self._check(end_pattern) and
               not (metadata := self._metadata())):
            buffer.append(self._advance())
        self._consume_newlines()

        front_extra = []
        if metadata:
            front_extra = buffer
            back = []
            while not self._is_at_end() and not self._check(end_pattern):
                back.append(self._advance())
            self._consume_newlines()
        else:
            back = buffer
        
        metadata = metadata if metadata else Metadata()

        return Card(front, metadata, back, front_extra)

    def _metadata(self) -> Metadata | None:
        metadata_pattern = "^```metadata"
        if self._is_at_end() or not self._match(metadata_pattern):
            return None
        
        res = []
        end_pattern = "^```"
        found_end = None
        while not self._is_at_end() and not (found_end := self._check(end_pattern)):
            res.append(self._advance())
        if found_end:
            self._advance()
            obj = {} if len(res) == 0 else json.loads("".join(res))
            return Metadata(**obj)
        else:
            raise ParserError(f"unclosed metadata block")

    def _consume_newlines(self):
        while not self._is_at_end() and self._peek() == "\n":
            self._advance()

    def _check(self, pattern: str) -> re.Match | None:
        return re.match(pattern, self._peek())

    def _match(self, pattern: str) -> re.Match | None:
        if (c := self._check(pattern)):
            self._current += 1
        return c

    def _peek(self) -> str:
        return self._lines[self._current]

    def _advance(self) -> str:
        self._current += 1
        return self._lines[self._current - 1]

    def _is_at_end(self) -> bool:
        return self._current >= len(self._lines)
