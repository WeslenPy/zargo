from zargo.block.back_reference_block import BackReferenceBlock
from zargo.block.length_block import LengthBlock
from .data_reader import DataReader


class BlockReader:

    def __init__(self, data):
        self.dataReader = DataReader(data)

    async def tryReadLength(self):
        old = await self.dataReader.getCurrentIndex()
        length = await self.dataReader.readVarLength()
        await self.dataReader.setCurrentIndex(old)
        return length

    async def readLength(self):
        return await self.dataReader.readVarLength()

    async def readBlock(self):
        value = await self.dataReader.readVarLength()

        if value < -3:
            adjValue = (-value) - 4
            if 0 <= adjValue < 4294967295:
                return BackReferenceBlock(adjValue)
        else:
            return LengthBlock(value)

    async def readBytes(self, length):
        return await self.dataReader.readBytes(length)
