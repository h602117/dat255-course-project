import requests
import json
import PIL.Image as Image
from ultralytics import YOLO
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY=os.getenv("API_KEY")

model = YOLO("yolov8m.pt")

# Just food related classes
classes = [ 46, 47, 48, 49, 50, 51, 52, 53, 54, 55 ]

def detect_objects(img):
    results = model([img], classes=classes)
    assert len(results) == 1, "Should get exactly one result"
    result = results[0]

    img_data = result.plot()
    img = Image.fromarray(img_data[..., ::-1])

    objects = {}
    for box in result.boxes:
        pred = box[0].cls[0].item()
        cls = result.names[pred]
        if cls in objects:
            objects[cls] += 1
        else:
            objects[cls] = 1

    objects = list(objects.items())

    nutr = ""
    for obj, cnt in objects:
        query = f"{cnt} {obj}"
        api_url = "https://api.api-ninjas.com/v1/nutrition?query={}".format(query)
        response = requests.get(api_url, headers={"X-Api-Key": API_KEY})
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            if len(data) == 0:
                nutr += f"{obj}: Could not find nutritional information\n"
                continue
            for d in data:
                cal = d["calories"]
                fat = d["fat_total_g"]
                pro = d["protein_g"]
                car = d["carbohydrates_total_g"]
                fib = d["fiber_g"]
                sug = d["sugar_g"]
                sod = d["sodium_mg"]
                pot = d["potassium_mg"]
                nutr += f"""{cnt} x {obj}:
- {cal} calories
- {fat} g fat
- {pro} g protein
- {car} g carbohydrates
- {fib} g fiber
- {sug} g sugar
- {sod} mg sodium
- {pot} mg potassium
--------------------------
"""

    return img, nutr


import gradio as gr

examples = [
    "./examples/bananas-and-apples.jpg",
    "./examples/oranges.webp",
    "./examples/broccoli-and-carrots.jpeg",
]

demo = gr.Interface(fn=detect_objects, inputs="image", outputs=["image", "textbox"], examples=examples)
demo.launch(inline=False)
