"""
Low-level library for Bluetooth LE connection to Brilliant Labs Frame and Halo devices (https://brilliant.xyz/)
"""
__all__ = ["brilliant_ble"]

from .brilliant_ble import BrilliantBle
from .brilliant_ble import BrilliantDeviceType
from .brilliant_ble import OtaError

__version__ = "3.1.0"
