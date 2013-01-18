import sys
import os
import select
import termios
from termios import *


class SerialException(Exception):
    pass


class SerialDisconnectException(SerialException):
    pass


class Serial:

    SPEED_MAP = { 9600: B9600, 115200: B115200 }

    def __init__(self, port, speed, **kwargs):
        self.port = port
        self.speed = speed
        self.open()

    def open(self):
        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY)
        iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(self.fd)
        print "tcgetattr result:", iflag, oflag, cflag, lflag, ispeed, ospeed, cc
        print "tcgetattr cc:", cc[VMIN], cc[VTIME]
        cc[VMIN] = 1
        iflag = IGNBRK
        oflag = 0
        cflag = CS8 | CREAD | CLOCAL | self.SPEED_MAP[self.speed]
        lflag = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])

    def write(self, data):
        os.write(self.fd, data)

    def read(self, size):
        buf = ""
        c = 0
        while size > 0:
            ready, _, _ = select.select([self.fd], [], [])
            assert ready
            chunk = os.read(self.fd, size)
            l = len(chunk)
            if l == 0:
                # If port was ready for read, but read 0 butes,
                # it means that it's gone (for example, underlying
                # hardware like USB adapter disconnected)
                raise SerialDisconnectException("Port disconnected")
            size -= l
            buf += chunk
            c += 1

        return buf
