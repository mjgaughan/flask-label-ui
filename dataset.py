
import csv
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List
import random

## TODO: configure this for yourself.
IDENTIFIER_FIELD = "id"

## What buttons should we show the user? Note: ``Other``` appears automatically.
DEFAULT_BUTTONS = ["Certainly Mutable", "Maybe Mutable", "Unsure", "Maybe Immutable", "Certainly Immutable"]

@dataclass
class Example:
    """This class holds a single example, in all it's weirdness."""

    """Your example MUST have a UNIQUE identifier. If your identifiers are numeric, just make them strings anyway."""
    id: str
    """This is the file path that was processed to read this example."""
    source_file: str
    """This is the row number from the source data file that generated the example."""
    source_line: int
    """Miscellaneous features; default: empty-dict"""
    features: Dict[str, Any] = field(default_factory=dict)

    def json_str(self) -> str:
        """ Not a very user-friendly way to view the data, but it's possible! """
        return json.dumps(self.features, indent=2, sort_keys=True)


def convert(source_file: str, source_line: int, data: Dict[str, Any]) -> Example:
    # TODO: MAYBE modify this part; which is the key?
    keep = Example(
        id=data[IDENTIFIER_FIELD],
        source_file=source_file,
        source_line=source_line,
        features=data,
    )
    return keep


def load_csv_examples(path: str) -> Dict[str, Example]:
    available = {}
    with open(path) as fp:
        rows = csv.reader(fp)
        header = next(rows)
        for i, row in enumerate(rows):
            keep = convert(path, i, dict(zip(header, row)))
            available[keep.id] = keep
    return available


def load_jsonl_examples(path: str) -> Dict[str, Example]:
    available = {}
    with open(path) as fp:
        for i, line in enumerate(fp):
            keep = convert(path, i, json.loads(line))
            available[keep.id] = keep
    return available


def load_examples() -> Dict[str, Example]:
    return load_csv_examples('trial_human_selected.csv')

if __name__ == '__main__':
    examples = load_examples()
    ids = list(examples.keys())
    random_id = random.choice(ids)
    print(examples[random_id])