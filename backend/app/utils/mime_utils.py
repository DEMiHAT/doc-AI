import filetype

def detect_mime(filepath: str) -> str:
    kind = filetype.guess(filepath)
    if kind is None:
        return "unknown"
    return kind.mime
