import time

import numpy as np
import cfscrape
from src.routes.nn.app.model.util import img_util as util
from src.routes.nn.app.model.tech.api import ModelApi
from src.routes.util.vectorSearch import VectorSearch
from fastapi import HTTPException


# imageServerURL = 'https://img.arz.ai'

def load_image(image_file,
               width=None,
               height=None,
               get_raw=False,
               mode_01=True,
               bgr=True,
               padding=255):
    """
    :param image_file: Image as numpy array or image URL
    :param width: Image width destination (optional)
    :param height: Image height destination (optional)
    :param get_raw: Return the raw image
    :param mode_01: Normalization mode True=[0-1], False=[-1,1], None=[0-255]
    :param bgr: Color schema
    :param padding: Color padding in the resize
    :return: A tuple of (raw image (if selected), raw shape, resized image)
    """
    ib = None
    if type(image_file) == bytes:
        ib = image_file
    elif type(image_file) == str:
        try:
            scraper = cfscrape.create_scraper()
            rq = scraper.get(image_file, timeout=2, stream=True)

            if int(rq.headers['Content-Length']) > 8000000 or 'image' not in rq.headers['Content-Type']:
                return ib, 'Invalid url'

            ib = rq.content
        except Exception as e:
            print(e)
            return ib, 'Invalid url'
    elif type(image_file) == np.ndarray:
        return util.img2ndarray(img=image_file, width=width, height=height, get_raw=get_raw,
                                mode_01=mode_01, bgr=bgr, padding=padding)
    return util.img2ndarray(img=ib, width=width, height=height, get_raw=get_raw, mode_01=mode_01,
                            bgr=bgr, padding=padding)


class Pic2Encoder(ModelApi):
    def inference(self, image_file):
        _, _, img = load_image(image_file, width=448, height=448, mode_01=None)
        if type(img) == str:
            return img

        _, resp = self.forward(img[None])  # .astype(np.float32)

        return resp.tolist()


class PicSearch(ModelApi):

    def __init__(self, name, uri_model):
        super().__init__(name, uri_model)
        self.search = VectorSearch()

    def prepare_response(self, rsp):
        payloads = rsp['results']['data']
        ok = []

        for i in payloads:
            o = {
                'id': i[0]
            }
            if i[-1] == 'danbooru':
                o['source'] = f'https://danbooru.donmai.us/posts/{i[0]}'
            elif i[-1] == 'gelbooru':
                o['source'] = f'https://gelbooru.com/index.php?page=post&s=view&id={i[0]}'
            elif i[-1] == 'zerochan':
                o['source'] = f'https://www.zerochan.net/{i[0]}'
            elif i[-1] == 'anime-pictures':
                o['source'] = f'https://anime-pictures.net/posts/{i[0]}'
            elif i[-1] == 'yande.re':
                o['source'] = f'https://yande.re/post/show/{i[0]}'
            elif i[-1] == 'e-shuushuu':
                o['source'] = f'https://e-shuushuu.net/image/{i[0]}'
            else:
                o['source'] = f'https://safebooru.org/index.php?page=post&s=view&id={i[0]}'

            o['score'] = i[1]

            o['pool'] = i[-1]
            ok.append(o)

        return ok

    def inference_url(self, image_file, limit=9, pool_id=None, mode_01=True):
        meta = {
            'api_version': '0.1.2',
            'mode': 'url/image'
        }
        st = time.time()
        if pool_id is None:
            pool_id = []
        _, _, img = load_image(image_file, width=448, height=448, mode_01=mode_01)
        if img is None:
            return None
        if type(img) == str:
            meta['status'] = {
                'code': 'ERROR',
                'msg': [
                    img
                ]
            }
            return meta
        st = time.time() - st
        meta['load_image_time'] = st

        time_embdeing, resp = self.forward(img[None])
        meta['embedding_time'] = time_embdeing

        time_search, payloads = self.search.search(vector=resp[0],
                                                   limit=limit,
                                                   pool_id=pool_id)
        # print(payloads)
        meta['latency_search'] = time_search - payloads['time']

        st = time.time()
        ok = self.prepare_response(rsp=payloads)
        st = time.time() - st

        meta['post_process_time'] = st

        meta['results'] = {
            'count': len(ok),
            'data': ok
        }
        payloads.pop('results')
        meta['search_meta'] = payloads

        meta['status'] = {
            'code': 'OK',
            'msg': []
        }

        return meta

    def inference_idx(self, pool, item_pool, item, limit=9):
        meta = {
            'api_version': '0.1.2',
            'mode': 'index'
        }

        time_search, payloads = self.search.search_by_id(pool=pool,
                                                         item_pool=item_pool,
                                                         item=item,
                                                         limit=limit)
        meta['latency_search'] = time_search - payloads['time']

        if payloads['status']['code'] != 'OK':
            raise HTTPException(status_code=404, detail=', '.join(payloads['status']['msg']))

        st = time.time()
        ok = self.prepare_response(rsp=payloads)
        st = time.time() - st
        meta['post_process_time'] = st

        meta['results'] = {
            'count': len(ok),
            'data': ok
        }
        payloads.pop('results')
        meta['search_meta'] = payloads
        return meta
