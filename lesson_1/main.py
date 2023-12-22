import asyncio

from pytoniq_core import Cell, StateInit, Builder, begin_cell, Address
from pytoniq import LiteClient, Contract, WalletV4R2

from secret import mnemo


code_boc = 'b5ee9c7241010c0100bd000114ff00f4a413f4bcf2c80b010201200302005af2d31fd33f31d31ff001f84212baf2e3e9f8000182107e8764efba9bd31f30f84201a0f862f002e030840ff2f0020148070402016e0605000db63ffe003f0850000db5473e003f08300202ce090800194f842f841c8cb1fcb1fc9ed5480201200b0a001d3b513434c7c07e1874c7c07e18b46000671b088831c02456f8007434c0cc1c6c244c383c0074c7f4cfcc4060841fa1d93beea6f4c7cc3e1080683e18bc00b80c2103fcbc208d1e30d3'
COUNTER_CODE = Cell.one_from_boc(code_boc)

data = begin_cell().store_uint(1, 32).store_uint(0, 32).end_cell()

state_init = StateInit(code=COUNTER_CODE, data=data)

address = Address((0, state_init.serialize().hash))

print(address.to_str(is_bounceable=True))


async def deploy():
    client = LiteClient.from_mainnet_config(7, trust_level=1)

    await client.connect()
    contract = await Contract.from_state_init(client, 0, state_init)

    wallet = await WalletV4R2.from_mnemonic(client, mnemo, 0)

    print(wallet)

    # result = await wallet.transfer(
    #     destination=address,
    #     amount=50000000,
    #     body=begin_cell()
    #         .store_uint(0x7e8764ef, 32)
    #         .store_uint(0, 64)
    #         .store_uint(10, 32)
    #         .end_cell(),
    # )

    # await contract.send_external(
    #     # state_init=state_init,
    #     body=begin_cell()
    #     .store_uint(0x7e8764ef, 32)
    #     .store_uint(0, 64)
    #     .store_uint(1, 32)
    #     .store_uint(10, 32)
    #     .end_cell()
    # )

    result = await contract.run_get_method(method='get_counter', stack=[])

    print(result)

    await client.close()

    # print(contract)


if __name__ == '__main__':
    asyncio.run(deploy())
