from pathlib import Path


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


def file_sorting(files: list[Path]) -> list[Path]:
    files.sort(key=value_file)
    return files
