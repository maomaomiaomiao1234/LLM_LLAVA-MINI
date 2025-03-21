import requests
import json
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_llava_api(image_path, prompt, controller_address="http://localhost:10000"):
    image_data = encode_image(image_path)

    data = {
        "model": "llava-v1.5-7b",  # 模型的名称（根据你的设置更改）
        #"model": "llava-mini",
        "images": [image_data],
        "prompt": prompt,
        "temperature": 0.7,  # 可选参数
        "top_p": 0.9,        # 可选参数
        "max_tokens": 512,   # 可选参数
        #"stop":"</s>"
    }
    response = requests.post(f"{controller_address}/worker_generate_stream", json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    #for line in response.iter_lines():
    #    if line:
    #        print(line.decode("utf-8"))

    #try:
    #    result = response.json()
    #    print(result["text"])
    #except requests.exceptions.JSONDecodeError as e:
    #    print(f"JSONDecodeError: {e}")

    #if response.status_code == 200:
    #    result = response.json()
    #    print(result["text"])
    #else:
    #    print(f"Error: {response.status_code} - {response.text}")

# 示例用法
#image_path = "/home/whang1234/Figure_1_newloss.png"
image_path = "/tmp/gradio/ed525b52861f0970f23499d799a8e324447eef1435a3f5526dec61c2fb42a39c/extreme_ironing.jpg"
prompt = "Describe this image. <image>"
call_llava_api(image_path, prompt)


