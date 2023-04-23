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
    ServiceID,
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
        """Create message to set the KNX USB Interface Device into cEMI mode"""
        packet_info = PacketInfo.from_data(PacketInfoData(SequenceNumber.FIRST_PACKET, PacketType.START_AND_END))
        knx_hid_report_body_data = KNXHIDReportBodyData(
            protocol_id=ProtocolID.BUS_ACCESS_SERVER_FEATURE_SERVICE,
            emi_id=ServiceID.DEVICE_FEATURE_SET,
            data=b"\x05\x03",  # message code, data
            partial=False)
        return KNXHIDFrame.from_data(KNXHIDFrameData(packet_info, knx_hid_report_body_data)).to_knx()

    def _prop_read_comm_mode(self):
        """Create message to read the KNX USB Interface Device communication mode"""
        packet_info = PacketInfo.from_data(PacketInfoData(SequenceNumber.FIRST_PACKET, PacketType.START_AND_END))
        knx_hid_report_body_data = KNXHIDReportBodyData(
        protocol_id=ProtocolID.KNX_TUNNEL,
        emi_id=ServiceID.DEVICE_FEATURE_SET,
        data=b"\xfc\x00\x08\x01\x34\x10\x01",  # message code, data (4.1.7.3.2 M_PropRead.req - PID_COMM_MODE)
        partial=False)
        return KNXHIDFrame.from_data(KNXHIDFrameData(packet_info, knx_hid_report_body_data)).to_knx()

    def _prop_write_comm_mode_data_link(self):
        """ """
        packet_info = PacketInfo.from_data(PacketInfoData(SequenceNumber.FIRST_PACKET, PacketType.START_AND_END))
        knx_hid_report_body_data = KNXHIDReportBodyData(
            protocol_id=ProtocolID.KNX_TUNNEL,
            emi_id=ServiceID.DEVICE_FEATURE_SET,
            data=b"\xf6\x00\x08\x01\x34\x10\x01\x00",  # message code, data (4.1.7.3.4 M_PropWrite.req - PID_COMM_MODE - 00h Data Link Layer)
            partial=False)
        return KNXHIDFrame.from_data(KNXHIDFrameData(packet_info, knx_hid_report_body_data)).to_knx()

    def run(self) -> None:
        """ """
        self.usb_device.write(self._set_cemi_mode())
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
