import os
import requests
import shutil
from tqdm import tqdm
from zipfile import ZipFile


def download_onnx(pth_model):
    url = pth_model.split('/')[-1]
    url = 'https://models.arz.ai/' + url + '.onnx'

    re = requests.get(url, stream=True)

    if not os.path.exists('/models'):
        os.makedirs('/models')

    file_size = int(re.headers.get('Content-Length', 0))

    with tqdm.wrapattr(re.raw, "read", total=file_size) as r:
        with open(pth_model + '.onnx', 'wb') as f:
            shutil.copyfileobj(r, f)


def download_qdrant_storage(pth: str, collection: str):
    url = 'https://models.arz.ai/' + collection + '.zip'

    re = requests.get(url, stream=True)

    if not os.path.exists(pth):
        os.makedirs(pth)

    file_size = int(re.headers.get('Content-Length', 0))
    sv = f'{pth}/{collection}.zip'

    if not os.path.exists(sv):
        with tqdm.wrapattr(re.raw, "read", total=file_size) as r:
            with open(sv, 'wb') as f:
                shutil.copyfileobj(r, f)

    with ZipFile(sv, "r") as zip_ref:
        for file in tqdm(iterable=zip_ref.namelist(), total=len(zip_ref.namelist())):
            zip_ref.extract(member=file, path=f'{pth}')

    os.remove(sv)
