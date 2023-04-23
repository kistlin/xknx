from __future__ import annotations

from enum import IntEnum


class SequenceNumber(IntEnum):
    """
    (3.4.1.2.2 Sequence number)
    0h            reserved; shall not be used
    other values  reserved; not used
    """

    FIRST_PACKET = 0x01
    SECOND_PACKET = 0x02
    THIRD_PACKET = 0x03
    FOURTH_PACKET = 0x04
    FIFTH_PACKET = 0x05


class DataSizeBySequenceNumber:
    """Returns the data size of the `KNX HID Report Body` by sequence number"""

    sizes: dict[SequenceNumber, int] = {
        SequenceNumber.FIRST_PACKET: 53,
        SequenceNumber.SECOND_PACKET: 61,
        SequenceNumber.THIRD_PACKET: 61,
        SequenceNumber.FOURTH_PACKET: 61,
        SequenceNumber.FIFTH_PACKET: 61,
    }

    @staticmethod
    def of(sequence_number: SequenceNumber) -> int:
        """ """
        return DataSizeBySequenceNumber.sizes.get(sequence_number, 0x00)


class PacketType(IntEnum):
    """
    (3.4.1.2.3 Packet type)
    all other values are reserved / not allowed
    """

    # START/END just as convenience for lookup, don't use!
    # START = 0x01  # (0001b)
    # END = 0x02  # (0010b)
    START_AND_END = 0x03  # (0011b)
    PARTIAL = 0x04  # (0100b)
    START_AND_PARTIAL = 0x05  # (0101b)
    PARTIAL_AND_END = 0x06  # (0110b)


class ProtocolID(IntEnum):
    """(3.4.1.3.4 Protocol identifiers)"""

    KNX_TUNNEL = 0x01
    M_BUS_TUNNEL = 0x02
    BATI_BUS_TUNNEL = 0x03
    BUS_ACCESS_SERVER_FEATURE_SERVICE = 0x0F


class EMIID(IntEnum):
    """(Coding of EMI ID octet (for “KNX Tunnel”))"""

    EMI1 = 0x01
    EMI2 = 0x02
    COMMON_EMI = 0x03


class ServiceID(IntEnum):
    """3.5.3.2 Device feature services"""

    RESERVED_NOT_USED_00 = 0x00
    DEVICE_FEATURE_GET = 0x01
    DEVICE_FEATURE_RESPONSE = 0x02
    DEVICE_FEATURE_SET = 0x03
    DEVICE_FEATURE_INFO = 0x04
    RESERVED_NOT_USED_EF = 0xEF
    RESERVED_NOT_USED_FF = 0xFF


class DeviceFeatures(IntEnum):
    """3.5.3.3 Device features"""
    SUPPORTED_EMI_TYPE = 0x01
    HOST_DEVICE_DEVICE_DESCRIPTOR_TYPE_0 = 0x02
    BUS_CONNECTION_STATUS = 0x03
    KNX_MANUFACTURER_CODE = 0x04
    ACTIVE_EMI_TYPE = 0x05
