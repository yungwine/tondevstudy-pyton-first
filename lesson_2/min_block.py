import asyncio
import logging

import requests
from pytoniq import LiteClient, LiteServerError


async def check_peer_block(client: LiteClient, seqno_from: int, seqno_to: int):
    seqno = (seqno_from + seqno_to) // 2
    if seqno_to - seqno_from <= 1:
        return seqno_to

    try:
        await client.lookup_block(-1, -2**63, seqno)
        print('exists', seqno)
        return await check_peer_block(client, seqno_from, seqno)
    except LiteServerError as e:
        print('not exists', seqno)
        if 'not in db' in e.message:
            return await check_peer_block(client, seqno, seqno_to)
        else:
            print(e)
    except Exception as e:
        print(e)


async def main():
    config = requests.get('https://ton.org/testnet-global.config.json').json()

    for i in range(len(config['liteservers'])):

        client = LiteClient.from_config(config, i, 2)

        try:
            await client.connect()
        except:
            print('SKIP CONNECTION', i)
            continue

        # print(await client.lookup_block(-1, -2**63, 34244942))

        last_seqno = await check_peer_block(client, 0, client.last_mc_block.seqno)

        print(f'LITESERVER {i} KNOWS {last_seqno}')

        # await client.lookup_block(-1, -2**63, 34244942)

        await client.close()


asyncio.run(main())
