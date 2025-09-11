from __future__ import annotations
from collections import deque
from statistics import mean
import struct
from typing import Tuple
import datetime
import uuid
import numpy as np
from timecode import Timecode
from constants.enum import FaceBlendShape


class PyLiveLinkFace:
    def __init__(self, name: str = "Python_LiveLinkFace", 
                        uuid: str = str(uuid.uuid1()), fps=60, 
                        filter_size: int = 5) -> None:

        # properties
        self.uuid = uuid
        self.name = name
        self.fps = fps
        self._filter_size = filter_size

        self._version = 6
        now = datetime.datetime.now()
        timcode = Timecode(
            self._fps, f'{now.hour}:{now.minute}:{now.second}:{now.microsecond * 0.001}')
        self._frames = timcode.frames
        self._sub_frame = 1056060032                
        self._denominator = int(self._fps / 60)     
        self._blend_shapes = [0.000] * 71
        self._old_blend_shapes = []                 
        for i in range(71):
            self._old_blend_shapes.append(deque([0.0], maxlen = self._filter_size))

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str) -> None:
        if not value.startswith("$"):
            self._uuid = '$' + value
        else:
            self._uuid = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int) -> None:
        if value < 1:
            raise ValueError("Only fps values greater than 1 are allowed.")
        self._fps = value

    def encode(self) -> bytes:        
        version_packed = struct.pack('<I', self._version)
        uuiid_packed = bytes(self._uuid, 'utf-8')
        name_lenght_packed = struct.pack('!i', len(self._name))
        name_packed = bytes(self._name, 'utf-8')

        now = datetime.datetime.now()
        timcode = Timecode(
            self._fps, f'{now.hour}:{now.minute}:{now.second}:{now.microsecond * 0.001}')
        frames_packed = struct.pack("!II", timcode.frames, self._sub_frame)  
        frame_rate_packed = struct.pack("!II", self._fps, self._denominator)
        data_packed = struct.pack('!B71f', 71, *self._blend_shapes)
        
        return version_packed + uuiid_packed + name_lenght_packed + name_packed + \
            frames_packed + frame_rate_packed + data_packed

    def get_blendshape(self, index: FaceBlendShape) -> float:     
        return self._blend_shapes[index.value]

    def set_blendshape(self, index: FaceBlendShape, value: float, 
                        no_filter: bool = True) -> None:
        if no_filter:
            self._blend_shapes[index.value] = value
        else:
            self._old_blend_shapes[index.value].append(value)
            filterd_value = mean(self._old_blend_shapes[index.value])
            self._blend_shapes[index.value] = filterd_value

    @staticmethod
    def decode(bytes_data: bytes) -> Tuple[bool, PyLiveLinkFace]:
        version = struct.unpack('<i', bytes_data[0:4])[0]
        uuid = bytes_data[4:41].decode("utf-8")
        name_length = struct.unpack('!i', bytes_data[41:45])[0]
        name_end_pos = 45 + name_length
        name = bytes_data[45:name_end_pos].decode("utf-8")
        if len(bytes_data) > name_end_pos + 16:

            #FFrameTime, FFrameRate and data length
            frame_number, sub_frame, fps, denominator, data_length = struct.unpack(
                "!if2ib", bytes_data[name_end_pos:name_end_pos + 17])

            if data_length != 71:
                raise ValueError(
                    f'Blend shape length is {data_length} but should be 71, something is wrong with the data.')

            data = struct.unpack(
                "!71f", bytes_data[name_end_pos + 17:])

            live_link_face = PyLiveLinkFace(name, uuid, fps)
            live_link_face._version = version
            live_link_face._frames = frame_number
            live_link_face._sub_frame = sub_frame
            live_link_face._denominator = denominator
            live_link_face._blend_shapes = data

            return True, live_link_face
        else:
            #print("Data does not contain a face, returning default empty face.")
            return False, PyLiveLinkFace()