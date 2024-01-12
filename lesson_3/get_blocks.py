import asyncio

from pytoniq import LiteBalancer


async def get_block():
    client = LiteBalancer.from_mainnet_config(2)
    await client.start_up()
    info = await client.get_masterchain_info()
    print(info)
    blk, block = await client.lookup_block(info['last']['workchain'], info['last']['shard'], info['last']['seqno'])
    print(blk, block)
    header = await client.raw_get_block_header(blk)
    print(header)
    print('#' * 30)
    full_block = await client.raw_get_block(blk)
    print(full_block.extra.account_blocks[0])
    await client.close_all()


async def get_block_transactions():
    client = LiteBalancer.from_mainnet_config(2)
    await client.start_up()
    info = await client.get_masterchain_info()
    blk, block = await client.lookup_block(info['last']['workchain'], info['last']['shard'], info['last']['seqno'])

    # trs = await client.raw_get_block_transactions(blk)
    # print(trs)
    # trs = await client.get_transactions(trs[0]['account'], 1, trs[0]['lt'], trs[0]['hash'])
    # print(trs)

    # trs = await client.raw_get_block_transactions_ext(blk)
    # print(trs)

    shards = await client.get_all_shards_info(blk)
    print(shards)

    for s in shards:
        shard_trs = await client.raw_get_block_transactions_ext(s)
        print(shard_trs)

    await client.close_all()


async def get_config():
    client = LiteBalancer.from_mainnet_config(2)
    await client.start_up()

    config = await client.get_config_all()
    config = await client.get_config_params(params=[12])
    print(config)

    await client.close_all()


asyncio.run(get_config())
