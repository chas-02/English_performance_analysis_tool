from paddleocr import PaddleOCR


class OCRrecognition:
    def __init__(self, use_gpu=False):
        self.PdOCR = PaddleOCR(use_angle_cls=True, use_gpu=use_gpu, lang='en')
    def ocr(self, img_path):
        try:
            print("====OCR START====")
            result = self.PdOCR.ocr(img_path, cls=True)
            return result
        except Exception as e:
            print("In OCRrecognition class -> ocr function:", e)
            return []