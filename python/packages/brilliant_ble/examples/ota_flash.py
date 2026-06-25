"""
Flashes signed app firmware to a Halo device over the BLE SMP (MCUmgr) OTA service.

Usage:
    python ota_flash.py zephyr.signed.bin                            # one-shot test boot (default)
    python ota_flash.py zephyr.signed.bin --dangerously-auto-confirm  # upload, confirm, reboot

By default the image is marked for a one-shot test boot: MCUboot reverts to the
previous firmware on the next reboot unless the new image is confirmed:
reconnect and call ota_confirm().

Note: first-time flashing and bootloader flashing still require the Alif wired
tools. This only updates a device that already boots an OTA-enabled app firmware.
"""
import argparse
import asyncio

from brilliant_ble import BrilliantBle, OtaError


async def main():
    parser = argparse.ArgumentParser(description="Flash signed app firmware to a Halo device over BLE SMP OTA")
    parser.add_argument("firmware", help="path to zephyr.signed.bin")
    parser.add_argument("--dangerously-auto-confirm", action="store_true", help="confirm the image immediately instead of marking it for a one-shot test boot")
    parser.add_argument("--chunk-size", type=int, default=384, help="upload payload bytes per packet (default 384)")
    args = parser.parse_args()

    def progress(sent, total):
        print(f"\rUploaded {sent}/{total} bytes ({sent * 100 // total}%)", end="", flush=True)

    halo = BrilliantBle()

    try:
        name = await halo.connect()
        print(f"Connected to {name}")

        image_hash = await halo.ota_flash_firmware(
            args.firmware,
            progress_handler=progress,
            confirm=args.dangerously_auto_confirm,
            chunk_size=args.chunk_size,
        )

        print(f"\nFlashed image with MCUboot hash {image_hash.hex()}")
        if not args.dangerously_auto_confirm:
            print("Image marked for test boot: after verifying the new firmware, reconnect and call ota_confirm() to keep it")
        print("Device is rebooting...")

    except OtaError as e:
        print(f"\nOTA update failed: {e}")
    except Exception as e:
        print(f"Not connected to Device: {e}")
    finally:
        await halo.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
