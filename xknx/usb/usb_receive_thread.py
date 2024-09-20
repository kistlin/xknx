from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from xknx.core.thread import BaseThread
from xknx.io.interface import CEMIBytesCallbackType
from xknx.usb.knx_hid_helper import KNXtoCEMI
from xknx.usb.util import USBDevice

if TYPE_CHECKING:
    from xknx.xknx import XKNX

logger = logging.getLogger("xknx.log")


class USBReceiveThread(BaseThread):
    """ """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        xknx: XKNX,
        usb_device: USBDevice,
        cemi_received_callback: CEMIBytesCallbackType,
    ):
        """ """
        super().__init__(name="USBReceiveThread")
        self._loop: asyncio.AbstractEventLoop = loop
        self._xknx = xknx
        self._usb_device: USBDevice = usb_device
        self._knx_to_telegram = KNXtoCEMI()
        self.cemi_received_callback = cemi_received_callback

    def run(self) -> None:
        """ """
        while self._is_active.is_set():
            usb_data = self._usb_device.read()
            done, cemi_frame = self._knx_to_telegram.process(usb_data)
            if done and cemi_frame:
                self._loop.call_soon_threadsafe(self.cemi_received_callback, cemi_frame)
