import time
from src.routes.nn.app.model.util.nn import nn

model = nn(pth_model='/models/wd-v1-4-convnext-encoder-v2',
           name='Pic2Encoder_512')


class ModelApi:
    def __init__(self, name, uri_model):
        self.model_name = name
        self.uri_model = uri_model

    def forward(self, x):
        st = time.time()
        inference = model.inference(x)
        print('Embedding_Time:\t ', time.time() - st)
        return time.time() - st, inference
