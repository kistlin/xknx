from __future__ import annotations

import logging
import queue
from queue import Queue
from typing import TYPE_CHECKING

from xknx.cemi import CEMIFrame
from xknx.core.thread import BaseThread
from xknx.usb.knx_hid_helper import KNXToUSBHIDConverter
from xknx.usb.util import USBDevice
from xknx.usb import (
    EMIID,
    ProtocolID,
    KNXHIDReportBodyData,
    KNXHIDFrame,
    KNXHIDFrameData,
    PacketType,
    PacketInfo,
    PacketInfoData,
    SequenceNumber,
)

if TYPE_CHECKING:
    from xknx.xknx import XKNX

logger = logging.getLogger("xknx.log")


class USBSendThread(BaseThread):
    """ """

    def __init__(self, xknx: XKNX, usb_device: USBDevice, queue: Queue[CEMIFrame]):
        """ """
        super().__init__(name="USBSendThread")
        self.xknx = xknx
        self.usb_device = usb_device
        self._queue = queue

    def _set_cemi_mode(self):
        """ """
        packet_info_data = PacketInfoData(SequenceNumber.FIRST_PACKET, PacketType.START_AND_END)
        packet_info = PacketInfo.from_data(packet_info_data)
        knx_hid_report_body_data = KNXHIDReportBodyData(
            protocol_id=ProtocolID.BUS_ACCESS_SERVER_FEATURE_SERVICE,
            # abuse the EMI ID 0x03, in this mode it means "Device Feature Set"
            emi_id=EMIID.COMMON_EMI,  # this is only an EMI ID if the protocol ID is 0x01 (KNX Tunnel)
            data=b"\x05\x03",
            partial=False)
        knx_hid_frame_data = KNXHIDFrameData(packet_info, knx_hid_report_body_data)
        hid_frame = KNXHIDFrame.from_data(knx_hid_frame_data)
        return hid_frame.to_knx()

    def _prop_read_comm_mode(self):
        """ """
        return b"\x01\x13\x0f\x00\x08\x00\x07\x01\x03\x00\x00\xfc\x00\x08\x01\x34" \
               b"\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def _prop_write_comm_mode_data_link(self):
        """ """
        return b"\x01\x13\x10\x00\x08\x00\x08\x01\x03\x00\x00\xf6\x00\x08\x01\x34" \
               b"\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
               b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def run(self) -> None:
        """ """
        data = self._set_cemi_mode()
        self.usb_device.write(data)
        self.usb_device.write(self._prop_write_comm_mode_data_link())
        while self._is_active.is_set():
            try:
                cemi_frame = self._queue.get(block=True)
                hid_frames = KNXToUSBHIDConverter.split_into_hid_frames(
                    cemi_frame.to_knx()
                )
                # after successful splitting actually send the frames
                for hid_frame in hid_frames:
                    self.usb_device.write(hid_frame.to_knx())
            except queue.Empty:
                pass
