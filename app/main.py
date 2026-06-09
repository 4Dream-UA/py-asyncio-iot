import time
import asyncio

from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService

async def run_sequence(service: IOTService, messages: list[Message]) -> None:
    """Виконує команди строго одна за одною."""
    for msg in messages:
        await service.send_msg(msg)

async def run_parallel(service: IOTService, messages: list[Message]) -> None:
    """Виконує всі команди одночасно."""
    async with asyncio.TaskGroup() as tg:
        for msg in messages:
            tg.create_task(service.send_msg(msg))

async def main() -> None:
    service = IOTService()

    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(service.register_device(hue_light))
        task2 = tg.create_task(service.register_device(speaker))
        task3 = tg.create_task(service.register_device(toilet))

    hue_light_id = task1.result()
    speaker_id = task2.result()
    toilet_id = task3.result()

    await run_parallel(service, [
        Message(hue_light_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.SWITCH_ON)
    ])
    await run_sequence(service, [
        Message(speaker_id, MessageType.PLAY_SONG, "Rick Astley - Never Gonna Give You Up")
    ])

    await run_sequence(service, [
        Message(toilet_id, MessageType.FLUSH),
        Message(toilet_id, MessageType.CLEAN)
    ])
    await run_parallel(service, [
        Message(hue_light_id, MessageType.SWITCH_OFF),
        Message(speaker_id, MessageType.SWITCH_OFF)
    ])


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()

    print(f"Elapsed: {end - start:.4f} seconds")
