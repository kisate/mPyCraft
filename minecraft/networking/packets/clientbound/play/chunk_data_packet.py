from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Integer, FixedPointInteger, Angle, UnsignedByte, Byte, Boolean, UUID,
    Short, VarInt, Double, Float, String, Enum, Difficulty, Dimension,
    GameMode, Vector, Direction, PositionAndLook, multi_attribute_alias,
    VarIntPrefixedByteArray, MutableRecord, Long
)

import numpy

GLOBAL_BITS_PER_BLOCK = 14 #TODO

class ChunkDataPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x20

    packet_name = 'chunk_data'
    class ChunkSection(MutableRecord):
        __slots__ = 'blocks', 'light', 'sky_light', 'palette', 'data'
        def __init__(self):
            self.blocks = numpy.zeros([16, 16, 16]).tolist()
            self.light = []
            self.sky_light = []
            self.data = None
        
        def update_block(self, x, y, z, data):
            self.blocks[x][y][z] = data

    class Chunk(MutableRecord):
        __slots__ = 'x', 'z', 'gu_continuous', 'bitmask', 'sections', 'entities', 'blocks_in_chunk'
        def __init__(self, x, z, gu_continuous, bitmask):
            self.x = x
            self.z = z
            self.gu_continuous = gu_continuous
            self.bitmask = bitmask
            self.sections = [ChunkDataPacket.ChunkSection()]*16
            self.entities = []
            self.blocks_in_chunk = [] #IDs that are in chunk

        def get_block(self, x, y, z):
            section_number = y // 16
            section = self.sections[section_number]
            return section.blocks[x - self.x*16][y % 16][z - self.z*16]

        def update_block(self, x, y, z, data):
            section_number = y // 16
            section = self.sections[section_number]
            section.update_block(x - self.x*16, y % 16, z - self.z*16, data)
            self.sections[section_number] = section
            self.update_blocks()

        def update_block_multi(self, records):
            for record in records:
                section_number = record.y // 16
                section = self.sections[section_number]
                section.update_block(record.x, record.y, record.z, record.blockId)
                self.sections[section_number] = section
            self.update_blocks()
        
        def update_blocks(self):
            self.blocks_in_chunk = []
            for section in self.sections:
                if section is not None:
                    blocks_in_section = []
                    for x in section.blocks:
                        for z in x:
                            for y in z:
                                if y not in blocks_in_section:
                                    blocks_in_section.append(y)
                    self.blocks_in_chunk = list(set(self.blocks_in_chunk) | set(blocks_in_section))
            # print(self.blocks_in_chunk)
            

        def __repr__(self):
            return 'chunk_x={}, chunk_z={}, blocks_in_chunk={}'.format(self.x, self.z, self.blocks_in_chunk)


    def read(self, file_object):
        # print('Reading chunk packet...')
        self.x = Integer.read(file_object)
        self.z = Integer.read(file_object)
        self.gu_continuous = Boolean.read(file_object)
        self.bitmask = VarInt.read(file_object)
        self.data_length = VarInt.read(file_object)
        self.chunk = ChunkDataPacket.Chunk(self.x, self.z, self.gu_continuous, self.bitmask)

        for i in range(16):
            if self.bitmask & (1 << i):
                bits_per_block = UnsignedByte.read(file_object)
                palette = None
                if bits_per_block < GLOBAL_BITS_PER_BLOCK:
                    palette_length = VarInt.read(file_object)
                    palette = []
                    for _ in range(palette_length):
                        palette.append(VarInt.read(file_object) // 16)

                section = ChunkDataPacket.ChunkSection()

                data_length = VarInt.read(file_object)
                data = b''
                for _ in range(data_length):
                    part = file_object.read(8)
                    data += part
                section.data = data
                section.palette = palette
                data = int.from_bytes(data, byteorder='big')
                
                for y in range(16):
                    for z in range(16):
                        for x in range(16):
                            block = data & ((1 << bits_per_block) - 1)
                            data = data >> bits_per_block
                            if palette is not None:
                                block = palette[block]
                
                            section.blocks[x][15 - y][15 - z] = block

                self.chunk.sections[i] = section
                
        self.chunk.update_blocks()
            # print(self.chunk.blocks_in_chunk)
                # print(s.data)
        # if len(self.chunk.blocks_in_chunk) > 1 : print(self.chunk.blocks_in_chunk)
        self.entities = VarIntPrefixedByteArray.read(file_object)
        # print('Reading chunk packet... Done')
