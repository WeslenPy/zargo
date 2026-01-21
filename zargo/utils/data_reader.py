from zargo.exception.data_exception import DataException

class DataReader:

    def __init__(self, data):
        self.data = data
        self.currentIndex = 0

    async def getCurrentIndex(self):
        return self.currentIndex

    async def setCurrentIndex(self, index):
        self.currentIndex = index

    async def getDataLength(self):
        return len(self.data)

    async def readByte(self):
        b = self.data[self.currentIndex]
        self.currentIndex += 1
        return b

    async def readBytes(self, length):

        if length < 0:
            raise DataException(-1, "LENGTH IS OUT OF BOUND")

        endIndex = self.currentIndex + length
        if endIndex > len(self.data):
            raise DataException(-1, "NOT ENOUGH DATA")

        ba = self.data[self.currentIndex:endIndex]
        self.currentIndex = endIndex
        return ba

    async def readVarLength(self):
        value = 0
        shift = 0

        while True:
            try:
                b = await self.readByte()
                tempValue = b & 0xFF

                if shift < 64:
                    value |= (tempValue & 0x7F) << shift
                    shift += 7

                    if (tempValue & 0x80) == 0:
                        # ZigZag decode
                        return (value >> 1) ^ -(value & 1)
                else:
                    # OVERFLOW IN VARLENGTH DECODING
                    return None

            except IndexError:
                # UNEXPECTED END OF DATA
                return None
