import typing as t


def iter_to_str(
    itr: t.Iterable,
    delimiter: str = ",",
) -> str:
    return delimiter.join(f"{_}" for _ in itr)
