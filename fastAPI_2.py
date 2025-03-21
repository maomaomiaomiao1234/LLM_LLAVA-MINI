import requests
import json
import base64
import re

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def stream_llava_response(api_url, payload):
    """Streams the LLaVA response and yields individual JSON objects."""
    with requests.post(api_url, json=payload, stream=True) as response:
        response.raise_for_status()
        buffer = ""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                buffer += decoded_chunk
                for match in re.finditer(r"\{[^{}]*(?:(?:\{[^{}]*\}[^{}]*)*)\}", buffer):
                    try:
                        json_obj = json.loads(match.group(0))
                        yield json_obj
                    except json.JSONDecodeError:
                        print(f"JSONDecodeError, but continuing.  Partial: {match.group(0)}")
                        continue
                buffer = buffer[match.end():]

def call_llava_api(image_path, prompt, controller_address="http://localhost:10000"):
    image_data = encode_image(image_path)

    data = {
        "model": "llava-mini",
        "images": [image_data],
        "prompt": prompt,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 512,
        "stop": "<\s>"
    }

    api_url = f"{controller_address}/worker_generate_stream"

    try:
        last_text = ""  # Store the text from the *last* JSON object
        for json_obj in stream_llava_response(api_url, data):
            if "text" in json_obj:
                last_text = json_obj["text"]  # Overwrite with the latest 'text'
            if "error_code" in json_obj and json_obj["error_code"] != 0:
                print(f"Error in stream: {json_obj}")
                #  Decide:  Do you want to stop if there's an error?
                #  If so, add a 'break' here.

        print(f"Last Response Text:\n{last_text}")  # Print only the *last* text

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
image_path = "/tmp/gradio/ed525b52861f0970f23499d799a8e324447eef1435a3f5526dec61c2fb42a39c/extreme_ironing.jpg"
prompt = "Describe this image. <image>"
call_llava_api(image_path, prompt)

