import asyncio
import time
import random
import json
import requests
from requests.exceptions import RequestException
from functools import partial

# 请求头部，仿照 WebUI 的请求头
headers = {
    "User-Agent": "LLaVA Client",  # 模拟 WebUI 中的 User-Agent
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
}

# 请求队列管理类
class RequestQueueManager:
    def __init__(self, max_requests=3, delay=10):
        # 设置队列最大并发数和请求间的延迟
        self.queue = asyncio.Queue()
        self.max_requests = max_requests
        self.delay = delay

    # 处理队列中的请求
    async def process_queue(self):
        while not self.queue.empty():
            model_name, worker_address, params = await self.queue.get()
            await self.worker_generate_stream(worker_address, params)
            await asyncio.sleep(self.delay)

    # 添加请求到队列
    async def add_request(self, model_name, worker_address, params):
        if self.queue.qsize() < self.max_requests:
            await self.queue.put((model_name, worker_address, params))
            print(f"Request added to queue. Current queue size: {self.queue.qsize()}")
        else:
            print("Queue is full. Please wait.")

    # 启动处理队列的线程
    async def start_processing(self):
        await self.process_queue()

    # 异步请求处理
    async def worker_generate_stream(self, worker_address: str, params: dict, retries=5, delay=30):
        print(f"Sending request to {worker_address} with params: {params}")
        if not worker_address.startswith("http://"):
            worker_address = "http://" + worker_address

        for attempt in range(retries):
            try:
                # 封装 POST 请求
                post_func = partial(requests.post, f"{worker_address}/worker_generate_stream", headers=headers, json=params, stream=True, timeout=10)
                response = await asyncio.get_event_loop().run_in_executor(None, post_func)

                if response.status_code == 200:
                    print("Generating text...")
                    for chunk in response.iter_lines(decode_unicode=True):
                        if chunk:
                            print(chunk)  # 输出生成的内容
                    break
                else:
                    print(f"Error: {response.status_code}")
            except RequestException as e:
                print(f"Request failed: {e}")

            # 使用指数退避和随机延迟
            if attempt < retries - 1:
                backoff_time = delay * (2 ** attempt) + random.uniform(0, 1)  # 增加一些随机性
                print(f"Retrying... ({attempt + 1}/{retries}) with delay {backoff_time} seconds")
                await asyncio.sleep(backoff_time)
            else:
                print("Max retries reached, unable to process request.")


# 获取模型列表
async def get_model_list(controller_url):
    try:
        post_func = partial(requests.post, f"{controller_url}/list_models")
        response = await asyncio.get_event_loop().run_in_executor(None, post_func)

        if response.status_code == 200:
            models = response.json()["models"]
            print("Available models:", models)
            return models
        else:
            print(f"Error: {response.status_code}")
            return None
    except RequestException as e:
        print(f"Request failed: {e}")
        return None


# 获取工作者地址
async def get_worker_address(controller_url, model_name):
    try:
        post_func = partial(requests.post, f"{controller_url}/get_worker_address", json={"model": model_name})
        response = await asyncio.get_event_loop().run_in_executor(None, post_func)

        if response.status_code == 200:
            worker_address = response.json().get("address")
            if worker_address:
                print(f"Worker address for model {model_name}: {worker_address}")
                return worker_address
            else:
                print("No worker address found.")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    except RequestException as e:
        print(f"Request failed: {e}")
        return None


# 主程序执行
async def main():
    controller_url = "http://localhost:10000"  # 控制器的地址
    models = await get_model_list(controller_url)
    if not models:
        print("No models found.")
        return

    model_name = models[0]  # 默认选择第一个模型
    worker_address = await get_worker_address(controller_url, model_name)
    if not worker_address:
        print(f"Unable to find worker address for model: {model_name}")
        return

    params = {
        "model": model_name,
        "prompt": "A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions. USER: hello ASSISTANT:",
        "temperature": 0.2,
        "top_p": 0.7,
        "max_new_tokens": 512,
        "stop": "</s>",
        "images": "List of 0 images: []"
    }

    # 初始化队列管理器
    queue_manager = RequestQueueManager(max_requests=1, delay=10)  # 最大1个请求并发，每个请求延迟10秒
    await queue_manager.add_request(model_name, worker_address, params)

    # 启动队列处理
    await queue_manager.start_processing()


if __name__ == "__main__":
    asyncio.run(main())
