import time
from src.routes.nn.app.model.util import qdrantEngine


id2boorus = {
    0: 'danbooru',
    1: 'gelbooru',
    2: 'zerochan',
    3: 'anime-pictures',
    4: 'yande.re',
    5: 'e-shuushuu',
    6: 'safebooru'
}


def _search(vector: list, pool, limit):
    gst = time.time()
    meta = {
        'search_version': '0.1.1',
    }

    st = time.time()
    data = qdrantEngine.search(vector=vector,
                               pool=pool,
                               limit=limit)

    if data['status']['code'] != 'OK':
        meta['status'] = {
            'code': 'ERROR',
            'msg': [
                'Failure in Qdrant API'
            ]
        }
        meta['qdrant_meta'] = data
        meta['time'] = time.time() - gst
        return meta

    res = data['results']['data']

    res.sort(key=lambda x: x[1], reverse=False)
    st = time.time() - st
    print('Search_Time:\t ', st)

    data.pop('results')
    meta['latency_search'] = st - data['time']
    meta['qdrant_meta'] = data

    meta['status'] = {
        'code': 'OK',
        'msg': []
    }
    meta['results'] = {
        'count': len(res),
        'data': res[:limit]
    }
    meta['time'] = time.time() - gst

    return meta


class VectorSearch():

    def search(self, vector, limit, pool_id: list):
        st = time.time()
        res = _search(vector.tolist(), pool_id, limit)
        st = time.time() - st
        print('Vector_Search:\t ', st)
        return st, res

    def search_by_id(self, pool, item_pool, item, limit):
        st = time.time()
        vector = qdrantEngine.get_vector(id2boorus[item_pool], item)
        res = _search(vector[0].vector, pool, limit)

        st = time.time() - st
        print('Vector_Search:\t ', st)

        return st, res
