import sys

sys.dont_write_bytecode = True

def return_tags(tags: list[str]) -> str:
    tags: str = "+".join(tags)