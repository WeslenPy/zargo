from zargo.struct import *
from zargo.utils import *
from .argo_data_decoder import ArgoDataDecoder
from .argo_wire_type_decoder import ArgoWireTypeDecoder
from zargo.exception.data_exception import DataException
from zargo.wiretype import *

class NoInstance(type):
    def __call__(self, *args, **kwargs):
        raise TypeError('STATIC CALL ONLY')


class ArgoMessageDecoder(metaclass=NoInstance):

    _schemaStore = None
    _schemaFile = None

    @staticmethod
    async def getArgoDataDecoder(data):
        reader = DataReader(data)

        b = await reader.readByte()
        if b & 0x80 == 0:
            inlineEverything = await Bitwise.isBitSet(b, 0)
            selfDescribing = await Bitwise.isBitSet(b, 1)
            outOfBandFieldErrors = await Bitwise.isBitSet(b, 2)
            selfDescribingErrors = await Bitwise.isBitSet(b, 3)
            nullTerminatedStrings = await Bitwise.isBitSet(b, 4)
            noDeduplication = await Bitwise.isBitSet(b, 5)
            hasUserFlags = await Bitwise.isBitSet(b, 6)

            userFlags = None
            if hasUserFlags:
                userFlags = []
                userFlagBytes = []
                bitCount = 0

                while True:
                    nextByte = await reader.readByte()
                    bitCount += 7
                    userFlagBytes.append(nextByte)
                    if nextByte & 0x01 == 0:
                        break

                if userFlagBytes:
                    for byte in reversed(userFlagBytes):
                        for pos in range(1, 8):
                            userFlags.append(await Bitwise.isBitSet(byte, pos))

            header = ArgoHeader(
                inlineEverything,
                selfDescribing,
                outOfBandFieldErrors,
                selfDescribingErrors,
                nullTerminatedStrings,
                noDeduplication,
                hasUserFlags,
                userFlags
            )

            argoBlock = ArgoBlock(header)

            remaining = await reader.getDataLength() - await reader.getCurrentIndex()

            if header.inlineEverything:
                inline = await reader.readBytes(remaining)
                argoBlock.byteQueue.append(inline)
            else:
                blockData = await reader.readBytes(remaining)

                blockReader = BlockReader(blockData)
                while True:
                    length = await blockReader.readLength()
                    if length is None:
                        break
                    bytes_ = await blockReader.readBytes(length)
                    argoBlock.byteQueue.append(bytes_)

            if not argoBlock.inlineEverything:
                return ArgoDataDecoder(
                    argoBlock,
                    BlockReader(argoBlock.byteQueue.pop()),
                    header
                )

        return None

    @staticmethod
    async def setSchemaFile(filepath):
        if (
            ArgoMessageDecoder._schemaFile is None
            or ArgoMessageDecoder._schemaFile != filepath
        ):
            ArgoMessageDecoder._schemaFile = filepath
            ArgoMessageDecoder._schemaStore = None

    @staticmethod
    async def loadSchemaFile():
        if ArgoMessageDecoder._schemaFile is None:
            raise DataException(-1, "SCHEMA FILE NOT SET")

        with open(ArgoMessageDecoder._schemaFile, "rb") as f:
            data = f.read()

        dataDecoder = await ArgoMessageDecoder.getArgoDataDecoder(data)
        wireTypeDecoder = ArgoWireTypeDecoder(dataDecoder)
        blockReader = dataDecoder.blockReader

        typeId = await blockReader.readLength()

        if typeId == 2:
            if ArgoMessageDecoder._schemaStore is None:
                ArgoMessageDecoder._schemaStore = {}

            length = await blockReader.readLength()
            for _ in range(length):
                key = await dataDecoder.decodeString()
                value = await wireTypeDecoder.decodeWireType()
                ArgoMessageDecoder._schemaStore[key] = value

    @staticmethod
    async def decodeMessage(schemaEntry, msgBytes):
        if ArgoMessageDecoder._schemaStore is None:
            await ArgoMessageDecoder.loadSchemaFile()

        if schemaEntry not in ArgoMessageDecoder._schemaStore:
            raise DataException(-1, "SCHEMA NAME ERROR")

        entryWireType = ArgoMessageDecoder._schemaStore[schemaEntry]
        dataDecoder = await ArgoMessageDecoder.getArgoDataDecoder(msgBytes)

        return await ArgoMessageDecoder.decodeTypeData(
            entryWireType,
            dataDecoder
        )

    @staticmethod
    async def decodeTypeData(wireType, dataDecoder):

        if isinstance(wireType, ArgoFieldWireType):
            return await ArgoMessageDecoder.decodeTypeData(
                wireType.type,
                dataDecoder
            )

        if isinstance(wireType, ArgoRecordWireType):
            obj = {}
            for key, value in wireType.fields.items():
                decoded = await ArgoMessageDecoder.decodeTypeData(
                    value,
                    dataDecoder
                )
                if decoded is not None:
                    obj[key] = decoded
            return obj

        if isinstance(wireType, ArgoScalarWireType):
            length = await dataDecoder.blockReader.tryReadLength()

            if length is None:
                return None

            if length == -2:
                await dataDecoder.blockReader.readLength()
                return None

            if wireType.type == ArgoScalarWireType.BOOLEAN:
                return await dataDecoder.decodeBoolean()
            if wireType.type == ArgoScalarWireType.STRING:
                return await dataDecoder.decodeString()
            if wireType.type == ArgoScalarWireType.VARINT:
                return await dataDecoder.decodeVarInt()

        if isinstance(wireType, ArgoBlockWireType):
            length = await dataDecoder.blockReader.tryReadLength()
            if length in (None, -2):
                return None
            return await dataDecoder.decodeBlock(wireType)

        if isinstance(wireType, ArgoArrayWireType):
            arr = []
            length = await dataDecoder.blockReader.tryReadLength()

            if length is None:
                return None
            if length == -2:
                return arr

            length = await dataDecoder.blockReader.readLength()
            for _ in range(length):
                arr.append(
                    await ArgoMessageDecoder.decodeTypeData(
                        wireType.type,
                        dataDecoder
                    )
                )
            return arr

        if isinstance(wireType, ArgoNullableWireType):
            typeId = await dataDecoder.blockReader.tryReadLength()

            if typeId in (-1, -2, -3, 0):
                await dataDecoder.blockReader.readLength()

            if typeId == -1:
                return None
            elif typeId == -3:
                return "ERROR"
            elif typeId == -2:
                return None
            else:
                return await ArgoMessageDecoder.decodeTypeData(
                    wireType.inner,
                    dataDecoder
                )

        return None
