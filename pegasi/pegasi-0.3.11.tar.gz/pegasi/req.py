import asyncio
from aiohttp import ClientSession
import multiprocessing

async def fetch(url, session,params={},json={}):
    async with session.post(url,params=params,json=json) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        #print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.text()
async def bound_fetch(sem, url, session,params={},json={}):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session,params,json)
async def run(urls,params=[],json=[]):
   
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i,url in enumerate(urls):
            # pass Semaphore and session to every GET request
            params_single=params[i] if i in list(map(lambda x: x[0],list(enumerate(params)))) else {}
            json_single=json[i] if i in list(map(lambda x: x[0],list(enumerate(json)))) else {}
          #  print("params_single",params_single)
            task = asyncio.ensure_future(bound_fetch(sem, url, session,params=params_single,json=json_single))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        return await responses
def chunks(arr,n): return list(map(lambda x:arr[x:][::n],range(0,n)))
def get_map(urls,params=[],json=[]):
    #print(params)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(urls,params,json))
    return loop.run_until_complete(future)
