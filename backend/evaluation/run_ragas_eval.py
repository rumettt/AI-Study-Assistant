import json
from pathlib import Path


def main() -> None:
    dataset = json.loads(Path("evaluation/golden_dataset.json").read_text())
    print("RAGAS evaluation placeholder")
    print(f"Loaded {len(dataset)} golden questions")
    print("Connect this script to a running API plus RAGAS metrics once production sample documents are available.")


if __name__ == "__main__":
    main()
