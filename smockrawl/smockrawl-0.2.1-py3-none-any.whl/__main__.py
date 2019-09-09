import sys
import getopt

import asyncio
import aiohttp

from smockrawl.smockrawl import Smockeo


def main ():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(loop, sys.argv[1:]))


async def crawl(loop, argv):
    username = None
    password = None
    detectorId = None

    try:
        opts, args = getopt.getopt(argv, "u:p:i:", ["username=", "password=", "id="])
    except getopt.GetoptError:
        print('Valid arguments: -u <username> -p <password> -i <sensorid>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-i", "--id"):
            detectorId = arg

    print("smockrawl - Smockeo crawler - CLI example")
    if not username:
        username = input("Smockeo username: ")
    if not password:
        password = input("Smockeo password: ")
    if not detectorId:
        detectorId = input("Smockeo detector ID: ")

    async with aiohttp.ClientSession() as session:
        smo = Smockeo(username, password, detectorId, loop, session)

        await smo.authenticate()
        await smo.poll()

        smo.print_status()

if __name__ == "__main__":
    main()
