# def hello():
#     v=yield 'hello'
#     print(v)
# gen=hello()
# result=gen.send(None)
# print(result)
# gen.send('world')

# def index_generator(L, target):
#     for i, num in enumerate(L):
#         if num == target:
#             yield i

# print(list(index_generator([1, 6, 2, 4, 5, 2, 8, 6, 3, 2], 2)))


# def is_des(a,b):
#     b=iter(b)
#     return all(i in b for i in a)
# print(is_des([1, 3, 5], [1, 2, 3, 4, 5]))

# import time
# import asyncio
# async def crawl_page(url):
#     print('crawling {}'.format(url))
#     sleep_time = int(url.split('_')[-1])
#     await asyncio.sleep(sleep_time)
#     print('OK {}'.format(url))

# async def main(urls):
#     tasks = [asyncio.create_task(crawl_page(url)) for url in urls]
#     await asyncio.gather(*tasks)
#     #for task in tasks:
#     #    await task
# start_time = time.perf_counter() 
# asyncio.run(main(['url_1', 'url_2', 'url_3', 'url_4']))
# end_time = time.perf_counter()
# print(end_time-start_time)



import asyncio
import time
async def worker_1():
    await asyncio.sleep(1)
    return 1

async def worker_2():
    await asyncio.sleep(2)
    return 2 / 0

async def worker_3():
    await asyncio.sleep(3)
    return 3

async def main():
    task_1 = asyncio.create_task(worker_1())
    task_2 = asyncio.create_task(worker_2())
    task_3 = asyncio.create_task(worker_3())

    await asyncio.sleep(2)
    task_3.cancel()

    res = await asyncio.gather(task_1, task_2, task_3, return_exceptions=True)
    print(res)

start_time = time.perf_counter() 
asyncio.run(main())
end_time = time.perf_counter()
print(end_time-start_time)