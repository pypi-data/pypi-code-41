import asyncio


@asyncio.coroutine
def shleepy_time(seconds):
    print("Shleeping for {s} seconds...".format(s=seconds))
    yield from asyncio.sleep(seconds)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Side note: Apparently, async() will be deprecated in 3.4.4.
    # See: https://docs.python.org/3.4/library/asyncio-task.html#asyncio.async
    tasks = asyncio.gather(
        asyncio.ensure_future(shleepy_time(seconds=5)),
        asyncio.ensure_future(shleepy_time(seconds=10)),
        return_exceptions=True
    )

    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")
        tasks.cancel()
        loop.run_forever()
    finally:
        loop.close()
