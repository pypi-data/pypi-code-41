import asyncio


def is_event_loop_exists():
    try:
        asyncio.get_event_loop()
        return True
    except RuntimeError:
        return False


def patch_event_loop():
    if not is_event_loop_exists():
        asyncio.set_event_loop(asyncio.new_event_loop())
