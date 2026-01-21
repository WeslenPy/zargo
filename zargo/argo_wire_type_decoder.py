from zargo.wiretype import *
from zargo.exception.data_exception import DataException


class ArgoWireTypeDecoder:

    def __init__(self, messageDecoder):
        self.messageDecoder = messageDecoder

    async def getWireTypeById(self, typeId):
        if typeId == -1:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.STRING)
        elif typeId == -2:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN)
        elif typeId == -3:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.VARINT)
        elif typeId == -4:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.FLOAT64)
        elif typeId == -5:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.BYTES)
        elif typeId == -6:
            return ArgoFixedWireType()
        elif typeId == -11:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.DESC)

        return None

    async def decodeNestedWireType(self):
        nestedTypeId = await self.messageDecoder.blockReader.readLength()
        nestedType = await self.getWireTypeById(nestedTypeId)

        if nestedType is None:
            return None

        key = await self.messageDecoder.decodeString()

        dedupe = await self.messageDecoder.argoBlock.getBlockData(
            "Boolean",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN),
                "Boolean",
                False
            )
        )
        
        dedupe = await dedupe.getData(self.messageDecoder.blockReader)

        return ArgoBlockWireType(nestedType, key, dedupe)

    async def decodeRecordWireType(self):
        fields = {}
        length = await self.messageDecoder.blockReader.readLength()

        for _ in range(length):
            wireType = await self.decode()
            fields[wireType.name] = wireType

        return ArgoRecordWireType(fields)

    async def decode(self):
        name = await self.messageDecoder.decodeString()
        wireType = await self.decodeWireType()

        omittable = await self.messageDecoder.argoBlock.getBlockData(
            "Boolean",
            ArgoBlockWireType(
                ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN),
                "Boolean",
                False
            )
        )
        
        omittable= await omittable.getData(self.messageDecoder.blockReader)

        return ArgoFieldWireType(wireType, name, omittable)

    async def decodeWireType(self):
        typeId = await self.messageDecoder.blockReader.readLength()

        if typeId == -1:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.STRING)
        elif typeId == -2:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.BOOLEAN)
        elif typeId == -3:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.VARINT)
        elif typeId == -4:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.FLOAT64)
        elif typeId == -5:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.BYTES)
        elif typeId == -6:
            return ArgoFixedWireType()
        elif typeId == -7:
            return await self.decodeNestedWireType()
        elif typeId == -8:
            return ArgoNullableWireType(inner=await self.decodeWireType())
        elif typeId == -9:
            return ArgoArrayWireType(type=await self.decodeWireType())
        elif typeId == -10:
            return await self.decodeRecordWireType()
        elif typeId == -11:
            return ArgoScalarWireType.getInstance(ArgoScalarWireType.DESC)
        elif typeId == -12:
            return ErrorWireType(DefaultWireType())
        elif typeId == -13:
            return PatchWireType(DefaultWireType())
        elif typeId == -15:
            return ExtensionWireType(DefaultWireType())

        raise DataException(-2, "WIRETYPE ERROR")
