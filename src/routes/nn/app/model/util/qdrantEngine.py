import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.routes.util.download import download_qdrant_storage
import time
import threading
import os

# %%
# START QDRANT SERVER
# pth_qdrant = './qdrant/storage'
pth_qdrant = '/api/qdrant/storage'
if not os.path.exists(pth_qdrant + '/raft_state'):
    download_qdrant_storage(pth=pth_qdrant, collection='booru_SW_v2_danbooru')


def qd():
    os.system("cd ./qdrant && ./qdrant")


threading.Thread(target=qd).start()

host = '127.0.0.1'
port = 6333

qdrant_client = QdrantClient(host=host, port=port)

collections = ["danbooru", "gelbooru", "zerochan", "anime-pictures", "yande.re", "e-shuushuu", "safebooru"]


# %%

def run(c, limit, vector):
    global payload
    search_result = qdrant_client.search(
        collection_name=c,
        query_vector=[float(x) for x in vector],
        limit=limit,
        with_payload=False,
        with_vectors=False,
        search_params=models.SearchParams(
            quantization=models.QuantizationSearchParams(
                ignore=False,
                rescore=False,
            )
        )
    )

    payload = payload + [[hit.id, hit.score, c] for hit in search_result]


def get_vector(collection, idx):
    result = qdrant_client.retrieve(
        collection_name=collection,
        ids=[int(idx)],
        with_vectors=True,
        with_payload=False
    )

    return result


def search(vector, limit, pool):
    global payload

    st = time.time()

    payload = []
    if len(pool) == 0:
        c = collections
    else:
        c = pool

    vector = np.array(vector)
    vector = (vector + 6) / 15
    vector = np.where(vector < 0, 0, vector)
    vector = np.where(vector > 1, 1, vector)

    for i in c:
        if i not in collections:
            return {
                'time': st,
                'version': '0.1.1',
                'status': {
                    'code': 'ERROR',
                    'msg': [
                        f"ERROR, collection {i} not found"
                    ]
                },
                'config': {
                    'limit': limit,
                    'pools': c,
                    'vector': [float(x) for x in vector]
                }
            }

    th = []
    for i in c:
        th.append(threading.Thread(target=run, args=[i, limit, vector]))
        th[-1].start()
    for i in th:
        i.join()

    payload.sort(key=lambda x: x[1], reverse=True)
    st = time.time() - st
    print('Qdrant time:\t ', st)

    meta = {
        'time': st,
        'qdrant_version': '1.1.0',
        'status': {
            'code': 'OK',
            'msg': []
        },
        'config': {
            'limit': limit,
            'pools': c,
            # 'vector': [float(x) for x in vector]
            'vector': []
        },
        'results': {
            'count': len(payload),
            'data': payload
        }
    }
    return meta
    # return payload
