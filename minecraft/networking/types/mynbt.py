from .basic import (
    Byte, Short, Integer, Long, Float, Double, UnsignedShort
)

def read_string(file_object):
    length = UnsignedShort.read(file_object)
    return file_object.read(length).decode('utf-8')

def read_tag(file_object, type_id, read_name=True):
    name = None
    if read_name :
        name = read_string(file_object)
    tag_payload = None
    if type_id == 1:
        tag_payload = Byte.read(file_object)
    elif type_id == 2:
        tag_payload = Short.read(file_object)
    elif type_id == 3:
        tag_payload = Integer.read(file_object)
    elif type_id == 4:
        tag_payload = Long.read(file_object)
    elif type_id == 5:
        tag_payload = Float(file_object)
    elif type_id == 6:
        tag_payload = Double(file_object)
    elif type_id == 7:
        length = Integer.read(file_object)
        tag_payload = []
        for _ in range(length):
            tag_payload.append(Byte.read(file_object))
    elif type_id == 8:
        tag_payload = read_string(file_object)
    elif type_id == 9:
        tags_type_id = Byte.read(file_object)
        length = Integer.read(file_object)
        tag_payload = []
        if length > 0:
            for _ in range(length):
                tag_payload.append(read_tag(file_object, tags_type_id, False)[1])
    elif type_id == 10:
        tag_payload = {}
        while True:
            tag_type_id = Byte.read(file_object)
            if tag_type_id == 0:
                break
            element = read_tag(file_object, tag_type_id)
            tag_payload[element[0]] = element[1]
    elif type_id == 11:
        length = Integer.read(file_object)
        tag_payload = []
        for _ in range(length):
            tag_payload.append(Integer.read(file_object))
    elif type_id == 12:
        length = Integer.read(file_object)
        tag_payload = []
        for _ in range(length):
            tag_payload.append(Integer.read(file_object))
    return (name, tag_payload)

def parse_bytes(file_object):
    result = {}
    
    while True:
        type_id = int.from_bytes(file_object.read(1), 'big')
        if type_id == 0:
            return result
        result = read_tag(file_object, type_id)[1]
        

