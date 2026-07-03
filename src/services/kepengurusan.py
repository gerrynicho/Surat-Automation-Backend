from src.repository import gas_client


async def get_kepengurusan_list() -> dict:
    return await gas_client._get("getKepengurusanList")
