from src.routes.nn.app.proyectos import Pic2Encoder
from fastapi import APIRouter
from fastapi import File

router = APIRouter()

model_p2e = Pic2Encoder(uri_model='pic2encoder',
                        name='Pic2Encoder_picsearch')


@router.get('/', include_in_schema=False)
async def get_pic2encoder():
    return model_p2e.get()


@router.get('/model', include_in_schema=False)
async def get_pic2encoder_model():
    return model_p2e.get_model()


@router.post('/')
async def post_Pic2Encoder_picsearch(image: bytes = File(
    description='jpg, png, webp format image'
)):
    """
    Generate the encoded vector for the similarity image search engine
    """
    re = model_p2e.inference(image)
    return re
