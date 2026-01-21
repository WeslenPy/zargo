from zargo.exception.data_exception import DataException
from zargo.wiretype.scalar import ArgoScalarWireType
from zargo.block import *


class ArgoBlockData(object):

    def __init__(self, wireType, header, data):
        self.block = None
        self.wireType = wireType

        if not header.inlineEverything:
            if self.wireType.wireType.type != ArgoScalarWireType.BOOLEAN:
                if wireType.dedupe and not header.hasUserFlags:
                    if data is not None:
                        self.block = DedupeBlock(header, data)
                        return
                    raise DataException(-2, "MISSING DATA")
                elif data is not None:
                    self.block = NormalBlock(header, data)
                else:
                    raise DataException(-2, "MISSING DATA")

        if data is None:
            self.block = InlineBlock(header)

    async def getVarInt(self, reader):
        if self.wireType.wireType.type == ArgoScalarWireType.VARINT:
            if isinstance(self.block, NormalBlock):
                length = await self.block.reader.readVarLength()
                return length

    async def getBoolean(self, reader):
        if self.wireType.wireType.type == ArgoScalarWireType.BOOLEAN:
            value = await reader.tryReadLength()

            if value == 1:
                await reader.readLength()
                return True
            elif value == 0:
                await reader.readLength()
                return False

            return False

    async def getBytes(self, reader):
        if self.wireType.wireType.type == ArgoScalarWireType.BYTES:

            if isinstance(self.block, DedupeBlock):
                block = await reader.readBlock()
                if block is not None:
                    if isinstance(block, BackReferenceBlock):
                        index = block.index
                        cache = self.block.cache
                        if index < len(cache):
                            return cache[int(index)]
                        raise DataException(-4, "INDEX ERROR")

                    elif isinstance(block, LengthBlock):
                        length = block.length
                        bytes_ = await self.block.reader.readBytes(length)
                        self.block.cache.append(bytes_)
                        return bytes_

            elif isinstance(self.block, InlineBlock):
                length = await reader.readLength()
                return await reader.readBytes(length)

            elif isinstance(self.block, NormalBlock):
                length = await reader.readLength()
                return await self.block.reader.readBytes(length)

            else:
                raise NotImplementedError("Unsupported block type.")

    async def getString(self, reader):
        if self.wireType.wireType.type == ArgoScalarWireType.STRING:

            if isinstance(self.block, DedupeBlock):
                block = await reader.readBlock()
                if block is not None:

                    if isinstance(block, BackReferenceBlock):
                        index = block.index
                        cache = self.block.cache
                        if index < len(cache):
                            str_block = cache[int(index)]
                            if isinstance(str_block, str):
                                return str_block
                            raise DataException(-3, "INVALID DATA")
                        return ""

                    elif isinstance(block, LengthBlock):
                        length = block.length
                        obj = await self.block.reader.readBytes(length)
                        decoded_str = obj.decode("utf-8")
                        self.block.cache.append(decoded_str)
                        return decoded_str

            elif isinstance(self.block, InlineBlock):
                block = await reader.readBlock()
                if block is not None:
                    return str(block)

            elif isinstance(self.block, NormalBlock):
                block = await reader.readBlock()
                if block is not None:
                    return str(block)

            else:
                raise NotImplementedError("Unsupported block type.")

        raise DataException(-5, "WIRETYPE ERROR")

    async def getData(self, reader):

        t = self.wireType.wireType.type

        if t == ArgoScalarWireType.STRING:
            return await self.getString(reader)

        if t == ArgoScalarWireType.BYTES:
            return await self.getBytes(reader)

        if t == ArgoScalarWireType.BOOLEAN:
            return await self.getBoolean(reader)

        if t == ArgoScalarWireType.FLOAT64:
            return await self.getFloat64(reader)

        if t == ArgoScalarWireType.VARINT:
            return await self.getVarInt(reader)

        return None
