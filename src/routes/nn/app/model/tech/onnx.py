import onnxruntime as rt
import numpy as np

print(rt.get_device())


class ModelONNX:
    """
    Batch inference not supported
    """

    def __init__(self, name, pth_model):
        self.model_name = name
        providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        self.model = rt.InferenceSession(pth_model, providers=providers)
        self.output_name = self.model.get_outputs()[0].name
        self.input_name = self.model.get_inputs()[0].name

    def forward(self, x):
        print(x.shape)
        onnx_pred = []
        for i in x[None]:
            onnx_pred.append(self.model.run([self.output_name], {self.input_name: i.astype(np.float32)})[0][0])

        return np.array(onnx_pred).astype(np.float32)

    def get(self):
        return 'onnx run ' + self.model_name

    def get_model(self):
        return 'onnx' + str(self.model.get_inputs()[0])
