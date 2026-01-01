import sys
from md_sink.parser import Parser
from md_sink.models import Deck, Card
from pathlib import Path

if len(sys.argv) < 2:
    print("usage: md-sink [path]")
    sys.exit(1)

d = Path(sys.argv[1])
if d.is_dir():
    all_cards: list[Card] = []
    for path in d.glob("**/*.md"):
        with open(path) as f:
            lines = f.readlines()
            parser = Parser(lines)
            sections = parser.parse()
            for section in sections:
                if isinstance(section, Deck):
                    for card in section.cards:
                        all_cards.append(card)

    print(all_cards[-3:])
else:
    from pprint import pprint
    with open(d) as f:
        pprint(Parser(f.readlines()).parse())
