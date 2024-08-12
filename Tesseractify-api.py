from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import pytesseract
import cv2
import base64
import io
import numpy as np

app = FastAPI()


class ImageData(BaseModel):
    image: str


def base64_2_image(base64_image_data: str) -> Image.Image:
    # decoding base64 to image
    try:
        image_data = base64.b64decode(base64_image_data)
        image_file = Image.open(io.BytesIO(image_data))
        return image_file
    except Exception as e:
        raise ValueError("Invalid base64 image data") from e


@app.post("/ocr")
async def perform_ocr(data: ImageData):
    try:
        # preprocessing image for better ocr accuracy
        image = base64_2_image(data.image)
        image_np = np.array(image)
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        image_pillow = Image.fromarray(gray_image)
        text = pytesseract.image_to_string(image_pillow, lang='eng')
        text_lines = text.splitlines()

        return {"recognized_texts": text_lines}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during OCR processing.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
