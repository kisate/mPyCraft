from minecraft.networking.packets import (
    Packet
)

from minecraft.networking.types import (
    Integer, FixedPointInteger, Angle, UnsignedByte, Byte, Boolean, UUID,
    Short, VarInt, Double, Float, String, Enum, Difficulty, Dimension,
    GameMode, Vector, Direction, PositionAndLook, multi_attribute_alias,
)

from minecraft.networking.types.utility import MutableRecord

from minecraft.networking.types import mynbt

class Slot(MutableRecord):
    __slots__ = 'item_id', 'item_count', 'item_damage', 'nbt_data'

    def __init__(self, item_id=None, item_count=None, item_damage=None, nbt_data=None):
        self.item_id = item_id
        if self.item_id != -1:
            self.item_count = item_count
            self.item_damage = item_damage
            self.nbt_data = nbt_data

    @staticmethod
    def read(file_object, read_all=True):
        item_id = Short.read(file_object)
        item_count = None
        item_damage = None
        nbt_data = None
        try: 
            if item_id != -1 and read_all:
                item_count = Byte.read(file_object)
                item_damage = Short.read(file_object)
                nbt_data = mynbt.parse_bytes(file_object)
        except BaseException as e:
            print(e)
        return Slot(item_id, item_count, item_damage, nbt_data)

class SetSlotPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x16

    packet_name = "set slot"
    def read(self, file_object):
        self.window_id = Byte.read(file_object)
        self.slot = Short.read(file_object)
        self.slot_data = Slot.read(file_object)