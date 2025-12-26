"""Deep module in subpackage for testing recursive expansion."""


class DeepClass:
    """Class in a nested subpackage."""

    async def deep_async_method(self, data: str) -> bool:
        return True

    def deep_sync_method(self) -> int:
        return 42
