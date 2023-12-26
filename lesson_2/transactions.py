import asyncio
import logging

from pytoniq import LiteClient, LiteBalancer, LiteServerError, WalletV4R2, begin_cell

from secret import mnemo

client = LiteBalancer.from_mainnet_config(1)


async def main():

    # logging.basicConfig(level=logging.INFO)

    await client.start_up()

    # wallet = await WalletV4R2.from_mnemonic(client, mnemo, 0)

    # await wallet.transfer(
    #     destination='EQB74UcMQwaO5cYmWQQL_9uI-UCcCdk0d8qK6Gwp8_vW16TV',
    #     amount=int(0.02 * 10**9),
    #     body=begin_cell().store_uint(0, 31).end_cell()
    # )

    trs = await client.get_transactions('UQCPCZU37-aComPLgaQBcOkevn4x5GJHSfZsFt6eF9DpHZH9', count=10)
    msg = trs[2].in_msg

    body = msg.body.begin_parse()

    if body.remaining_bits > 32:
        op_code = body.load_uint(32)
        if op_code == 0x7362d09c:
            query_id = body.load_uint(64)
            amount = body.load_coins()
            sender = body.load_address()
            forward_payload = body
            print(query_id, amount, sender, forward_payload)

    await client.close_all()


asyncio.run(main())
