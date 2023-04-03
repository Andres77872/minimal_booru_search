from src.routes.nn.app.model.tech.onnx import ModelONNX as onnx
from src.routes.util.download import download_onnx
import os


class nn:
    def __init__(self, pth_model, name):
        self.name = name
        if not os.path.exists(pth_model + '.onnx'):
            download_onnx(pth_model=pth_model)
        self.model = onnx(pth_model=pth_model + '.onnx', name=self.name)

    def get(self):
        return {
            'app': self.name,
            'model': self.model.get()}

    def getModel(self):
        return self.model.get_model()

    def inference(self, x):
        return self.model.forward(x)
