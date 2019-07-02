"""
zippy_refresh will try to download a bit of the ZS program, so that ZS will reset the 30 days timer.
Put all the ZS links in txt files in the same folder or sub-folder of this program, then run this program.

Require *requests*
_pip install requests_
"""
import glob
import itertools
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
from timeit import timeit


# change this to how many concurrent threads
THREADS=16


re_fileid = re.compile(r'https?://(\w+\.zippyshare\.com)/./(\w+)/', re.IGNORECASE)
re_vara = re.compile(r'var a = (\d+)')
re_varb = re.compile(r'var b = (\d+)')
re_varc = re.compile(r'a \+ (\d+)%b')
def fetch(session, url):
    with session.get(url) as response:
        data = response.text
        if response.status_code == 200:
            try:
                a=int(re_vara.search(data).group(1))
                b=int(re_varb.search(data).group(1))
                c=int(re_varc.search(data).group(1))
                d = int(int(a/3) + c % int(b/3))
                # print(a, b, c, d)

                m = re_fileid.search(url)
                url2 = "https://%s/d/%s/%d/file.html" % (m.group(1), m.group(2), d)
                resp2 = session.head(url2)
                # print(resp2.headers)

                print("SUCCESS: %s"%(url))
            except:
                print("FAILURE: %s" % (url))
        else:
            print("FAILURE: %s"%(url))


async def main():
    urls = itertools.chain(*[open(file).read().splitlines() for file in glob.glob('*.txt', recursive=True)])
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url)
                )
                for url in urls
            ]
            for response in await asyncio.gather(*tasks):
                pass


loop = asyncio.get_event_loop()
t=timeit(lambda:loop.run_until_complete(asyncio.ensure_future(main())), number=1)
print("Completed in %f sec"%t)
