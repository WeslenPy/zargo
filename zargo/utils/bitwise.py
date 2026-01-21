

class Bitwise:

    @staticmethod
    async def isBitSet(value: int, bit_position: int) -> bool:
        return (value & (1 << bit_position)) != 0

    @staticmethod
    async def isValidShift(value: int, shift: int) -> bool:
        return (value & 0x80) != 0 and shift <= 63

    @staticmethod
    async def decodeZigzag(value: int) -> int:
        return (value >> 1) ^ -(value & 1)
