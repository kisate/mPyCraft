from minecraft.networking.packets import (
    Packet
)

from minecraft.networking.types import (
    Integer, FixedPointInteger, Angle, UnsignedByte, Byte, Boolean, UUID,
    Short, VarInt, Double, Float, String, Enum, Difficulty, Dimension,
    GameMode, Vector, Direction, PositionAndLook, multi_attribute_alias,
)

from minecraft.networking.types.utility import MutableRecord

from minecraft.networking.types import Slot

from nbt import nbt

WINDOW_SIZES = {
    0 : 46,
}

class WindowItemsPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x14

    packet_name = "window items"
    def read(self, file_object):
        self.window_id = UnsignedByte.read(file_object)
        self.count = Short.read(file_object)
        self.slots = [Slot(-1)]*self.count
        for slot_number in range(self.count):
            self.slots[slot_number] = Slot.read(file_object)

class SetSlotPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x16

    packet_name = "set slot"
    definition = [
        {'window_id' : Byte},
        {'slot' : Short},
        {'slot_data' : Slot}
    ]

class ConfirmTransactionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x11

    packet_name = 'confirm transaction cb'
    definition = [
        {'window_id' : Byte},
        {'action_number' : Short},
        {'accepted' : Boolean}
    ]
    
class HeldItemChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x3A
    
    packet_name = 'held item change cb'
    definition = [
        {'slot' : Byte}
    ]