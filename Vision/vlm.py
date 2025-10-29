import base64
import io
import json
import os
from PIL.Image import Image
from openai import OpenAI
from openai.types.shared_params import ResponseFormatJSONObject, ResponseFormatText


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



class VLM:

    _system_prompt: str = None
    _enable_thinking: bool = False


    def __init__(self, openai_client: OpenAI, model: str, *, max_tokens: int=2048, temperature: float=0.3):
        self.client = openai_client
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def set_system_prompt(self, prompt: str):
        self._system_prompt = prompt

    def detect_bbox(self, image: Image, *, json_mode=True, prompt=None, wh=(1024, 1024)):
        image.thumbnail(wh)
        byte_io = io.BytesIO()
        image.save(byte_io, format='JPEG')
        base64_str = base64.b64encode(byte_io.getvalue()).decode('utf-8')
        messages = [
            {"role": "system", "content": self._system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}
                    }
                ],
            }
        ]
        response_format: ResponseFormatText = {"type": "text"}
        if json_mode:
            response_format: ResponseFormatJSONObject = {"type": "json_object"}
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                response_format=response_format,
            )
            result = completion.choices[0].message.content
            print(result)
            if json_mode:
                return json.loads(result)
            else:
                return result
        except Exception as e:
            print(f"[错误] 调用 API 或解析 JSON 时出错: {e}")
            raise e


def detect_bbox_from_vlm(client, image_path, class_name, *, prompt=None, json_mode=True):
    """调用 API 获取单个图片的 Bounding Box"""
    system_prompt = f'''
You are a helpful assistant to detect objects in images.
Use JSON array format to output the bounding box of the target object.
JSON return example:

[
	{{"bbox_2d": [65, 91, 497, 493], "label": "{class_name}"}},
	{{"bbox_2d": [330, 133, 1011, 680], "label": "{class_name}"}}
]
'''
    try:
        base64_image = encode_image(image_path)
        prompt = prompt or f"检测图片中所有的蘑菇，当有多个蘑菇时，将每个蘑菇都单独框选出来, label 为：{class_name}，以 JSON 格式输出。"
        print(prompt)
        completion = client.chat.completions.create(
            model=os.getenv("VL_MODEL"),
            max_tokens=2048,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ],
                }
            ],
            response_format={"type": "json_object"},
        )
        result = completion.choices[0].message.content
        if json_mode:
            print('detect result:', result)
            return json.loads(result)
        else:
            return result
    except Exception as e:
        print(f"  [错误] 调用 API 或解析 JSON 时出错: {e}")
        return None
