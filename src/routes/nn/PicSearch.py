from src.routes.nn.app.proyectos import PicSearch
from fastapi import APIRouter, Request, Form, File, HTTPException

import time

router = APIRouter()

model_p2s = PicSearch(uri_model='pic2encoder',
                      name='picSearch')

boorus = ['danbooru']
boorus2id = {
    'danbooru': 0
}


def prepare_params(limit, pool):
    if limit is None:
        limit = 9
    if pool is None:
        pool = []
    else:
        """
        IDK how to send a list in a Form from react, with a request from python works fine but its work
        """
        if len(pool) == 1 and (',' in pool[0] or pool[0] == ''):
            if pool[0] == '':
                pool = boorus
            elif ',' in pool[0]:
                pool = pool[0].split(',')
            else:
                return None, f"Pool '{pool}' not allowed (Empty = All or {', '.join(boorus)})"

        for i in pool:
            if i not in boorus:
                return None, f"Pool '{i}' not allowed (Empty = All or {', '.join(boorus)})"
    limit = int(limit)
    if 0 > limit > 128:
        limit = 9
    return limit, pool


def search(image, limit, pool, mode_01=None):
    global_time = time.time()
    r = model_p2s.inference_url(image_file=image, limit=limit, pool_id=pool, mode_01=mode_01)
    global_time = time.time() - global_time
    return global_time, r


@router.post('/url', description='Search by url image')
def post_PicSearch_by_url(image: str = Form(), limit=Form(9)):
    limit, pool = prepare_params(limit=limit, pool=['danbooru'])

    if limit is None:
        return pool

    global_time, r = search(image=image, limit=limit, pool=pool, mode_01=None)
    if r['status']['code'] != 'OK':
        raise HTTPException(status_code=422, detail=', '.join(r['status']['msg']))
    r['time'] = global_time
    return r


@router.post('/image', description='Search by image png, jpg or webp')
def post_PicSearch(image: bytes = File(), limit=Form(9)):
    limit, pool = prepare_params(limit=limit, pool=['danbooru'])

    if limit is None:
        return pool

    global_time, r = search(image=image, limit=limit, pool=pool, mode_01=None)
    if r is None:
        raise HTTPException(status_code=422, detail='Unprocessed image input')

    r['time'] = global_time
    return r


@router.post('/', description='Search by post id, at the momento only work with danbooru')
def get_query(image_id=Form(1),
              limit=Form(9)):
    limit, pool = prepare_params(limit=limit, pool=['danbooru'])

    if type(pool) == str:
        raise HTTPException(status_code=422, detail=pool)

    if type(limit) is int and 0 < limit <= 128:
        try:
            r = model_p2s.inference_idx(pool=pool, item_pool=0, item=image_id, limit=limit)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=422, detail="Query not found")

        return r
    else:
        raise HTTPException(status_code=422, detail="Limit search not allowed")
