from zargo.struct.argo_block import ArgoBlock
from zargo.struct.argo_header import ArgoHeader
from zargo.utils.block_reader import BlockReader
from zargo.wiretype.block import ArgoBlockWireType
from zargo.wiretype.scalar import ArgoScalarWireType


class ArgoDataDecoder:

    def __init__(self, argoBlock:ArgoBlock, blockReader:BlockReader, argoHeader:ArgoHeader):
        self.argoBlock = argoBlock
        self.blockReader = blockReader
        self.argoHeader = argoHeader

    async def decodeVarInt(self):
        result=  await self.argoBlock.getBlockData(
            "Int",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoScalarWireType.VARINT),
                "Int",
                False
            )
        )
        
        return await result.getData(
            self.blockReader
        )

    async def decodeString(self):
        result =  await self.argoBlock.getBlockData(
            "String",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoScalarWireType.STRING),
                "String",
                True
            )
        )
        
        return await result.getData(
            self.blockReader
        )

    async def decodeBoolean(self):
        result =  await self.argoBlock.getBlockData(
            "Boolean",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN),
                "Boolean",
                False
            )
        )
        
        
        return await result.getData(
            self.blockReader
        )

    async def decodeBytes(self):
        result= await self.argoBlock.getBlockData(
            "Bytes",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoBlockWireType.BYTES),
                "Bytes",
                False
            )
        )
        
          
        return await result.getData(
            self.blockReader
        )
        
        
        
    async def decodeBlock(self, wt):

        wireType = wt.wireType

        if isinstance(wireType, ArgoScalarWireType):

            if wireType.type == ArgoScalarWireType.VARINT:
                return await self.decodeVarInt()

            if wireType.type == ArgoScalarWireType.STRING:
                blockData = await self.argoBlock.getBlockData(
                    wt.key,
                    ArgoBlockWireType(
                        ArgoScalarWireType.getInstance(ArgoScalarWireType.STRING),
                        "String",
                        True
                    )
                )

                if blockData is None:
                    return None
                return await blockData.getData(self.blockReader)

            if wireType.type == ArgoScalarWireType.BOOLEAN:
                result =  await self.argoBlock.getBlockData(
                    "Boolean",
                    ArgoBlockWireType(
                        ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN),
                        "Boolean",
                        False
                    )
                )
                
                return await result.getData(
                    self.blockReader
                )

            if wireType.type == ArgoScalarWireType.BYTES:
                result =  await self.argoBlock.getBlockData(
                    wt.key,
                    ArgoBlockWireType(
                        ArgoScalarWireType.getInstance(ArgoScalarWireType.BYTES),
                        "Bytes",
                        False,
                    )
                )
                
                return await result.getData(
                    self.blockReader
                )

