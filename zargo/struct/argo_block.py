from zargo.wiretype.scalar import ArgoScalarWireType
from zargo.struct.argo_block_data import ArgoBlockData


class ArgoBlock(object):

    def __init__(self, header):
        self.header = header
        self.byteQueue = []
        self.typeBlockMap = {}
        self.inlineEverything = header.inlineEverything

    async def getBlockData(self, key, wireType):
        blockData = self.typeBlockMap.get(key)
        if blockData is not None:
            return blockData

        header = self.header

        if (
            not header.inlineEverything
            and not (
                isinstance(wireType.wireType, ArgoScalarWireType)
                and wireType.wireType.type == ArgoScalarWireType.BOOLEAN
            )
        ):
            if len(self.byteQueue) == 0:
                return None

            newBlockData = ArgoBlockData(
                wireType,
                self.header,
                self.byteQueue.pop(0)
            )
        else:
            newBlockData = ArgoBlockData(
                wireType,
                self.header,
                None
            )

        self.typeBlockMap[key] = newBlockData
        return newBlockData
