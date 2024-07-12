from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import io
import cv2
import numpy as np
from PIL import Image

app = FastAPI()

@app.post("/remove_blank_rows")
async def remove_blank_rows(file: UploadFile = File(...), threshold: int = 10, spacing: int = 6):
    image = Image.open(io.BytesIO(await file.read()))
    image_np = np.array(image)

    processed_image = process_image(image_np, threshold, spacing)
    processed_image_pil = Image.fromarray(processed_image)

    buf = io.BytesIO()
    processed_image_pil.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

def process_image(image_np, threshold, spacing):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np

    threshold = threshold
    spacing = spacing

    rows_to_remove = []
    consecutive_blank_rows = []

    for i in range(gray.shape[0]):
        if np.std(gray[i, :]) < threshold:
            consecutive_blank_rows.append(i)
        else:
            if len(consecutive_blank_rows) >= spacing:
                rows_to_remove.extend(consecutive_blank_rows[spacing:])
            consecutive_blank_rows = []

    if len(consecutive_blank_rows) >= spacing:
        rows_to_remove.extend(consecutive_blank_rows[spacing:])

    cleaned_image = np.delete(image_np, rows_to_remove, axis=0)

    return cleaned_image