from typing import Dict, List

from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.util.bech32m import encode_puzzle_hash
from chia.util.byte_types import hexstr_to_bytes
from chia.util.ints import uint128


class SimulatorFullNodeRpcClient(FullNodeRpcClient):
    async def farm_block(self, target_ph: bytes32, number_of_blocks: int = 1, guarantee_tx_block: bool = False) -> None:
        address = encode_puzzle_hash(target_ph, "txch")
        await self.fetch(
            "farm_block", {"address": address, "blocks": number_of_blocks, "guarantee_tx_block": guarantee_tx_block}
        )

    async def set_auto_farming(self, set_auto_farming: bool) -> bool:
        result = await self.fetch("set_auto_farming", {"auto_farm": set_auto_farming})
        result = result["auto_farm_enabled"]
        assert result == set_auto_farming
        return bool(result)

    async def get_auto_farming(self) -> bool:
        result = await self.fetch("get_auto_farming", {})
        return bool(result["auto_farm_enabled"])

    async def get_farming_ph(self) -> bytes32:
        result = await self.fetch("get_farming_ph", {})
        return bytes32(hexstr_to_bytes(result["puzzle_hash"]))

    async def get_all_coins(self, include_spent_coins: bool = False) -> List[CoinRecord]:
        json_result = await self.fetch("get_all_coins", {"include_spent_coins": include_spent_coins})
        return [CoinRecord.from_json_dict(coin_records) for coin_records in json_result["coin_records"]]

    async def get_all_puzzle_hashes(self) -> Dict[bytes32, uint128]:
        str_result = (await self.fetch("get_all_puzzle_hashes", {}))["puzzle_hashes"]
        return {bytes32.from_hexstr(ph): uint128(amount) for (ph, amount) in str_result.items()}

    async def revert_blocks(self, num_of_blocks_to_delete: int = 1, delete_all_blocks: bool = False) -> int:
        request = {"delete_all_blocks": delete_all_blocks, "num_of_blocks": num_of_blocks_to_delete}
        return int((await self.fetch("revert_blocks", request))["new_peak_height"])

    async def reorg_blocks(
        self, num_of_blocks_to_revert: int = 1, num_of_new_blocks: int = 1, revert_all_blocks: bool = False
    ) -> int:
        request = {
            "revert_all_blocks": revert_all_blocks,
            "num_of_blocks_to_rev": num_of_blocks_to_revert,
            "num_of_new_blocks": num_of_new_blocks,
        }
        return int((await self.fetch("reorg_blocks", request))["new_peak_height"])
