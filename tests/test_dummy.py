def a(b: int) -> int:
    return b * 2


a("adf")  # type: ignore[arg-type]
