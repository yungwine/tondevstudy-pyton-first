import asyncio

from pytoniq import LiteBalancer, Contract, WalletV4R2
from pytoniq_core import StateInit, begin_cell, HashMap, Slice, Address
import hashlib


def hash_str(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest(), 'big')


keys = {
    hash_str('name'): 'name',
    hash_str('description'): 'description',
    hash_str('image'): 'image',
    hash_str('symbol'): 'symbol',
    hash_str('decimals'): 'decimals'
}


def get_key(key: str):
    return keys.get(int(key, 2))


def parse_content(content: Slice):
    tag = content.load_uint(8)
    if tag == 1:
        url = content.load_snake_string()
        return {'url': url}
    elif tag == 0:
        metadata = content.load_dict(256, key_deserializer=get_key, value_deserializer=lambda src: src.load_snake_string())
        return metadata


async def parse_jetton(client: LiteBalancer, addr: str):
    result = await client.run_get_method(addr, 'get_jetton_data', [])
    return {'total_supply': result[0], 'owner': result[2].load_address(), 'metadata': parse_content(result[3].begin_parse())}


async def get_jetton_wallet_address(client: LiteBalancer, jetton: str, owner_address: str):
    owner_address_slice = begin_cell().store_address(owner_address).to_slice()
    result = await client.run_get_method(jetton, 'get_wallet_address', [owner_address_slice])
    return result[0].load_address()


async def get_jetton_wallet_data(client: LiteBalancer, address: Address):
    result = await client.run_get_method(address, 'get_wallet_data', [])
    return {'balance': result[0], 'owner': result[1].load_address(), 'jetton_master': result[2].load_address()}


async def main():
    client = LiteBalancer.from_mainnet_config(2)
    await client.start_up()

    addr = 'EQAS_C1H0b0LLr4eX7ICuX80mxwg2DaBOnAB1JCA4-HNrYv_'

    parsed = await parse_jetton(client, addr)
    print(parsed)

    jetton_wallet_addr = await get_jetton_wallet_address(client, addr, 'UQCPCZU37-aComPLgaQBcOkevn4x5GJHSfZsFt6eF9DpHZH9')
    print(jetton_wallet_addr)

    jetton_wallet_data = await get_jetton_wallet_data(client, jetton_wallet_addr)
    print(jetton_wallet_data)

    await client.close_all()


if __name__ == '__main__':
    asyncio.run(main())
