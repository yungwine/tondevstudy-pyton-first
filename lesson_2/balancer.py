import asyncio
import logging

from pytoniq import LiteClient, LiteBalancer, LiteServerError

client = LiteBalancer.from_mainnet_config(1)


async def main():

    # logging.basicConfig(level=logging.INFO)

    await client.start_up()

    try:
        await client.lookup_block(wc=-1, shard=-2**63, seqno=10, choose_random=True)
    except LiteServerError as e:
        print(e.code)
        print(e.message)

    await client.close_all()


asyncio.run(main())
