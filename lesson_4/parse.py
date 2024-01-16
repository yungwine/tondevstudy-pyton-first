import asyncio

from pytoniq import LiteBalancer, RunGetMethodError
from pytoniq_core import Slice, Cell, begin_cell

from mint import get_content

col_addr = 'EQDyWZIoTXuEUaM6ROtnKs0lmtkJVWEg1vXMimm_A_rdMIyE'
# nft_addr = 'EQCfrd-zvf8fiEt6F0a7u4uYB0qLZLyMZnviDmzCyBEHjKAZ'
nft_addr = 'EQD2Y4i9ounFr1Gm6XGUelNciCPa-hywqGAZDvg_nX3WvJup'


async def get_collection_data(client: LiteBalancer):
    stack = await client.run_get_method(col_addr, 'get_collection_data', [])
    content_cell: Slice = stack[1].begin_parse()
    if content_cell.preload_uint(8) == 1:
        content_cell.skip_bits(8)
        content_url = content_cell.load_snake_string()
        return {'next_item_index': stack[0], 'content': content_url, 'owner': stack[2].load_address()}


async def get_nft_address_by_index(client: LiteBalancer, index: int):
    stack = await client.run_get_method(col_addr, 'get_nft_address_by_index', [index])
    return stack[0].load_address()


async def get_royalty_params(client: LiteBalancer):
    stack = await client.run_get_method(col_addr, 'royalty_params', [])
    return {'royalty_factor': stack[0], 'royalty_base': stack[1], 'royalty_address': stack[2].load_address()}


async def get_nft_content(client: LiteBalancer, index: int, individual_nft_content: Cell):
    stack = await client.run_get_method(col_addr, 'get_nft_content', [index, individual_nft_content])
    return stack[0].begin_parse().load_snake_string()


async def get_nft_data(client: LiteBalancer):
    stack = await client.run_get_method(nft_addr, 'get_nft_data', [])
    return {'init': stack[0], 'index': stack[1], 'collection_address': stack[2].load_address(), 'owner_address': stack[3].load_address(), 'content': stack[4]}


async def get_sale_data(client: LiteBalancer, address):
    stack = await client.run_get_method(address, 'get_sale_data', [])
    print(stack)
    if stack[0] == 0x46495850:
        return {'is_complete': stack[1], 'created_at': stack[2], 'marketplace_address': stack[3].load_address(), 'nft_address': stack[4].load_address(), 'nft_owner_address': stack[5].load_address()}
    elif stack[0] == 0x415543:
        return {'end': stack[1], 'end_time': stack[2], 'marketplace_address': stack[3].load_address(), 'nft_address': stack[4].load_address(), 'nft_owner_address': stack[5].load_address()}


async def get_nft_sale(client: LiteBalancer):
    nft_data = await get_nft_data(client)
    try:
        return await get_sale_data(client, nft_data['owner_address'])
    except RunGetMethodError:
        print('not on sale')


async def main():
    client = LiteBalancer.from_mainnet_config(2)
    await client.start_up()

    col_data = await get_collection_data(client)

    for i in range(0, col_data['next_item_index']):
        print(await get_nft_address_by_index(client, i))

    # print(await get_nft_address_by_index(client, 0))
    # print(await get_royalty_params(client))
    # print(await get_nft_content(client, 0, nft_data['content']))
    # print(nft_data)

    # print(await get_nft_sale(client))

    await client.close_all()


asyncio.run(main())
