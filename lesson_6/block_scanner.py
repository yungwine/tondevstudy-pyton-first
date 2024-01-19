import asyncio
import json
import logging
import time
from types import coroutine
from collections import deque

from pytoniq_core import Cell, Slice, MessageAny, Transaction, Address
from pytoniq_core.tlb.block import ExtBlkRef

from pytoniq.liteclient import RunGetMethodError
from pytoniq.liteclient import LiteClient
from pytoniq_core.tlb import Block, ValueFlow, ShardAccounts
from pytoniq_core.tl import BlockIdExt
from pytoniq.liteclient.balancer import LiteBalancer


class BlockScanner:

    def __init__(self,
                 client: LiteClient,
                 block_handler: coroutine
                 ):
        """
        :param client: LiteClient
        :param block_handler: function to be called on new block
        """
        self.client = client
        self.block_handler = block_handler
        self.shards_storage = {}
        self.blks_dequeue = deque()
        self.inited = False

    async def run(self):
        if not self.client.inited:
            raise Exception('should init client first')
        master_blk = self.mc_info_to_tl_blk(await self.client.get_masterchain_info())
        if not self.inited:
            shards = await self.client.get_all_shards_info(master_blk)
            for shard in shards:
                self.shards_storage[self.get_shard_id(shard)] = shard.seqno
                self.blks_dequeue.append(shard)
            self.inited = True
        while True:
            self.blks_dequeue.append(master_blk)

            shards = await self.client.get_all_shards_info(master_blk)
            for shard in shards:
                await self.get_not_seen_shards(shard)
                self.shards_storage[self.get_shard_id(shard)] = shard.seqno

            tasks = []
            while self.blks_dequeue:
                tasks.append(self.block_handler(self.blks_dequeue.pop()))

            await asyncio.gather(*tasks)

            last_seqno = master_blk.seqno
            while True:
                new_master_blk = self.mc_info_to_tl_blk(await self.client.get_masterchain_info_ext())
                if new_master_blk.seqno != last_seqno:
                    master_blk = new_master_blk
                    break

    async def get_not_seen_shards(self, shard: BlockIdExt):
        if self.shards_storage.get(self.get_shard_id(shard)) == shard.seqno:
            return []
        result = []
        self.blks_dequeue.append(shard)
        full_blk = await self.client.raw_get_block_header(shard)
        prev_ref = full_blk.info.prev_ref
        if prev_ref.type_ == 'prev_blk_info':  # only one prev block
            prev: ExtBlkRef = prev_ref.prev
            await self.get_not_seen_shards(BlockIdExt(
                    workchain=shard.workchain, seqno=prev.seqno, shard=shard.shard,
                    root_hash=prev.root_hash, file_hash=prev.file_hash
                )
            )
        else:
            prev1: ExtBlkRef = prev_ref.prev1
            prev2: ExtBlkRef = prev_ref.prev2
            await self.get_not_seen_shards(BlockIdExt(
                    workchain=shard.workchain, seqno=prev1.seqno, shard=shard.shard,
                    root_hash=prev1.root_hash, file_hash=prev1.file_hash
                )
            )
            await self.get_not_seen_shards(BlockIdExt(
                    workchain=shard.workchain, seqno=prev2.seqno, shard=shard.shard,
                    root_hash=prev2.root_hash, file_hash=prev2.file_hash
                )
            )
        return result

    @staticmethod
    def mc_info_to_tl_blk(info: dict):
        return BlockIdExt.from_dict(info['last'])

    @staticmethod
    def get_shard_id(blk: BlockIdExt):
        return f'{blk.workchain}:{blk.shard}'


async def handle_block(block: BlockIdExt):
    if block.workchain == -1:  # skip masterchain blocks
        return
    trs = await client.raw_get_block_transactions_ext(block)
    print(block.seqno, ':', len(trs))
    for tr in trs:
        if not tr.in_msg:  # skip external messages
            continue
        cs = tr.in_msg.body.begin_parse()
        if cs.remaining_bits < 32:
            continue
        op_code = cs.load_uint(32)
        if op_code == 0x178d4519:
            cs.skip_bits(64)
            amount = cs.load_coins()
            from_addr = cs.load_address()
            jetton_wallet_addr = Address((block.workchain, tr.account_addr))
            from jettons import get_jetton_wallet_data, parse_jetton
            try:
                data = await get_jetton_wallet_data(client, jetton_wallet_addr)
                minter_data = await parse_jetton(client, data['jetton_master'])
                print('JETTON', jetton_wallet_addr, from_addr, amount, data, minter_data)
            except RunGetMethodError:
                continue
        if op_code == 0x7362d09c:
            cs.skip_bits(64)
            amount = cs.load_coins()
            from_addr = cs.load_address()
            print(amount, from_addr)


client = LiteBalancer.from_mainnet_config(trust_level=1)


async def main():
    await client.start_up()
    client.set_max_retries(3)
    scanner = BlockScanner(client=client, block_handler=handle_block)
    exc_num = 0
    while True:
        try:
            await scanner.run()
        except Exception as e:
            exc_num += 1
            print(e, type(e))
            if exc_num > 10:
                exc_num = 0
                await client.close_all()
                await asyncio.sleep(1)
                await client.start_up()
            continue


if __name__ == '__main__':
    asyncio.run(main())
