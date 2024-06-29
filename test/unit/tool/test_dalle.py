# 2024/6/29
# zhangzhong
import base64
from io import BytesIO
from test.utils import painting_tool

from PIL import Image

from app.tool import painting


def test_painting_tool():
    # class ImagesResponse(BaseModel):
    # created: int
    # data: List[Image]

    # class Image(BaseModel):
    # b64_json: Optional[str] = None
    # """
    # The base64-encoded JSON of the generated image, if `response_format` is
    # `b64_json`.
    # """
    # revised_prompt: Optional[str] = None
    # """
    # The prompt that was used to generate the image, if there was any revision to the
    # prompt.
    # """
    # url: Optional[str] = None
    # """The URL of the generated image, if `response_format` is `url` (default)."""

    response = painting.dalle(prompt="draw a cute cat")
    print(response.created)
    print(len(response.data))
    for image in response.data:
        print(image.revised_prompt)
        if image.url:
            print(image.url)
        if image.b64_json:
            # Step 1: Decode the base64 string
            image_bytes = base64.b64decode(image.b64_json)
            # Step 2: Create an image from the decoded bytes
            image_data = BytesIO(image_bytes)
            image = Image.open(image_data)
            # Step 3: Save the image to a file
            image.save(
                "output_image.png"
            )  # Specify your desired output image file name and format


def test_painting_tool_draw_background():
    painting_tool.draw(
        # prompt="A photo of an astronaut riding a horse in the space"
        prompt="A logo for a website that is about AI and agent, background should be white. this logo should be simple and elegant"
        # prompt="draw a picture that should contains element of universe, AI. color should be blue and black."
    )
