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

        def get_block(self, x, y, z, relative=False):
            section_number = y // 16
            section = self.sections[section_number]
            if relative:
                return section.blocks[x][y % 16][z]
            else:
                return section.blocks[x - self.x*16][y % 16][z - self.z*16]

        def update_block(self, x, y, z, data, relative=True):
            section_number = y // 16
            section = self.sections[section_number]
            if relative:
                section.update_block(x, y % 16, z, data)
            else:
                section.update_block(x - self.x*16, y % 16, z - self.z*16, data)
            self.sections[section_number] = section
            self.update_blocks()

        def update_block_multi(self, records):
            for record in records:
                section_number = record.y // 16
                section = self.sections[section_number]
                section.update_block(record.x, record.y % 16, record.z, record.blockId)
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
        def read_data(self, data, dimension):
            with open('temp.txt', 'wb') as f:
                f.write(data)
            with open('temp.txt', 'rb') as file_object:
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
                        data = []
                        for _ in range(data_length):
                            part = file_object.read(8)
                            data.append(int.from_bytes(part, 'big'))
                        section.data = data
                        section.palette = palette
                        
                        block_mask = (1 << bits_per_block) - 1
                        
                        # print(i)

                        for y in range(16):
                            for z in range(16):
                                for x in range(16):
                                    block_mask = (1 << bits_per_block) - 1
                                    number = (((y << 4) + z) << 4) + x
                                    long_number = (number*bits_per_block) >> 6
                                    bit_in_long_number = (number*bits_per_block) & 63
                                    block = (data[long_number] >> bit_in_long_number) & (block_mask)
                                    if bit_in_long_number + bits_per_block > 64:
                                        block |= (data[long_number + 1] & ((1 << (bit_in_long_number + bits_per_block - 64)) - 1)) << (64 - bit_in_long_number)
                                    if palette:
                                        # if block > 0:
                                        #     print(palette)
                                        #     print(len(palette))
                                        #     print(block)
                                        #     print(bits_per_block)
                                        #     print((x, y, z, self.x, self.z))
                                        block = palette[block]
                        
                                    section.blocks[x][y][z] = block
                            
                        section.light = file_object.read(2048)
                        if dimension == 0:
                            section.sky_light = file_object.read(2048)

                        self.sections[i] = section
                    
            self.update_blocks()

        def __repr__(self):
            return 'chunk_x={}, chunk_z={}, blocks_in_chunk={}'.format(self.x, self.z, self.blocks_in_chunk)


    def read(self, file_object):
        # print('Reading chunk packet...')
        self.x = Integer.read(file_object)
        self.z = Integer.read(file_object)
        self.gu_continuous = Boolean.read(file_object)
        self.bitmask = VarInt.read(file_object)
        self.data_length = VarInt.read(file_object)
        self.data = file_object.read(self.data_length)
        self.chunk = ChunkDataPacket.Chunk(self.x, self.z, self.gu_continuous, self.bitmask)
        self.entity_data_length = VarInt.read(file_object)
        self.entitity_data = file_object.read(self.entity_data_length) #TODO

            # print(self.chunk.blocks_in_chunk)
                # print(s.data)
        # if len(self.chunk.blocks_in_chunk) > 1 : print(self.chunk.blocks_in_chunk)
        
        # print('Reading chunk packet... Done')
