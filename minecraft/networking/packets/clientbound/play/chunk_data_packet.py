from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Integer, FixedPointInteger, Angle, UnsignedByte, Byte, Boolean, UUID,
    Short, VarInt, Double, Float, String, Enum, Difficulty, Dimension,
    GameMode, Vector, Direction, PositionAndLook, multi_attribute_alias,
    VarIntPrefixedByteArray, MutableRecord, Long
)

GLOBAL_BITS_PER_BLOCK = 14 #TODO

class ChunkDataPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x20

    packet_name = 'chunk_data'
    
    class ChunkSection(MutableRecord):
        __slots__ = 'bits_per_block', 'blocks', 'light', 'sky_light'
        def __init__(self, bits_per_block):
            self.bits_per_block = bits_per_block
            self.blocks = []
            self.light = []
            self.sky_light = []

    class Chunk(MutableRecord):
        __slots__ = 'x', 'z', 'gu_continuous', 'bitmask', 'sections', 'entities'
        def __init__(self, x, z, gu_continuous, bitmask):
            self.x = x
            self.z = z
            self.gu_continuous = gu_continuous
            self.bitmask = bitmask
            self.sections = []
            self.entities = []

    def read(self, file_object):
        self.x = Integer.read(file_object)
        self.z = Integer.read(file_object)
        self.gu_continuous = Boolean.read(file_object)
        self.bitmask = VarInt.read(file_object)
        self.data_length = VarInt.read(file_object)
        self.chunk = ChunkDataPacket.Chunk(self.x, self.z, self.gu_continuous, self.bitmask)

        for i in range(16):
            if self.bitmask & (1 << i):
                bits_per_block = UnsignedByte.read(file_object)
                print(bits_per_block)
                palette = None
                if bits_per_block < GLOBAL_BITS_PER_BLOCK:
                    palette_length = VarInt.read(file_object)
                    palette = []
                    for _ in range(palette_length):

                        palette.append(VarInt.read(file_object) // 16)

                section = ChunkDataPacket.ChunkSection(bits_per_block)

                data_length = VarInt.read(file_object)
                # print(data_length)
                data = b''
                for _ in range(data_length):
                    part = file_object.read(8)
                    # print(part)
                    data += part
                data = int.from_bytes(data, byteorder='big')
                while data > 0:
                    # print(data)
                    block = data & ((1 << bits_per_block) - 1)
                    data = data >> bits_per_block
                    if palette is not None:
                        # print(palette)
                        
                        block = palette[block]
                    section.blocks.append(block)
                self.chunk.sections.append(section)
        self.entities = VarIntPrefixedByteArray.read(file_object)
