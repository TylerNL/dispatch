from app.ingest.base import Source


async def run_once(source: Source) -> int:
    raise NotImplementedError


async def run_all() -> dict[str, int]:
    raise NotImplementedError


def start_scheduler() -> None:
    raise NotImplementedError
