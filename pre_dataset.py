import json

dataset_content = """
[
    {
        "id": "Cargi-628d-4724-b370-b84de974a19f",
        "image": "data_self/Pembroke_and_Cardigan_Welsh_Corgi.jpg",
        "conversations": [
            {
                "from": "human",
                "value": "<image>\nWho is in the picture?"
            },
            {
                "from": "gpt",
                "value": "This image features two distinct breeds of Welsh Corgi – the Pembroke and the Cardigan. Captured in a high-resolution photograph, the dogs are presented side by side against a soft, neutral background that accentuates their unique characteristics. The Pembroke, typically known for its shorter, more compact frame and often docked tail, contrasts with the Cardigan’s slightly longer body and naturally long, bushy tail. The lighting highlights the texture of their coats and the expressive nature of their eyes, showcasing both their playful charm and dignified stance as working herding dogs."
            }
        ]
    }
]
"""

with open("data_self/Corgi.json", "w") as f:
    f.write(dataset_content)

