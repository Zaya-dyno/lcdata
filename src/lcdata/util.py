from pathlib import Path
import re


def letter_to_number(letter: str) -> int:
    return ord(letter.lower()) - ord("a") + 1


def value_file(file: Path) -> int:
    file_name = file.stem
    file_parts = file_name.split("_")
    n = 0
    n = n * 26 + letter_to_number(file_parts[0])
    n = n * 26 + letter_to_number(file_parts[1][0])
    n = n * 10 + int(str(file_parts[1][1:]))
    n = n * 2 + int(file_parts[2].lower() != "raw")
    return n


def compare_file_names_key(file: Path):
    """
    Returns a tuple for sorting based on the file name pattern:
    [A]_[B][number]_[raw|subtracted]
    """
    name = file.stem
    regex = re.compile(r"^([A-Z])_([A-Z])(\d+)_(raw|subtracted)$", re.IGNORECASE)
    match = regex.match(name)
    if not match:
        # Fallback: sort lexicographically if pattern doesn't match
        return (name,)
    first_letter = match.group(1).upper()
    second_letter = match.group(2).upper()
    number = int(match.group(3))
    raw_or_sub = 0 if match.group(4).lower() == "raw" else 1
    return (first_letter, second_letter, number, raw_or_sub)


def file_sorting(files: list[Path]) -> list[Path]:
    files.sort(key=compare_file_names_key)
    return files
