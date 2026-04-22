async def send_email(to: str, subject: str, html: str, text: str) -> None:
    raise NotImplementedError


async def send_digest_to_subscribers(html: str, text: str) -> int:
    raise NotImplementedError
