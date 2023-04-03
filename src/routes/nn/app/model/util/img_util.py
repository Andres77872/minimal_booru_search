import numpy as np
import cv2


def resize(raw: np.ndarray, width: int = 256, height: int = 256, get_raw: bool = False, padding: int = 255):
    p = max(raw.shape[:2] / np.array([height, width]))
    s = raw.shape[:2]
    r = s / p

    img = cv2.resize(raw, (int(r[1]), int(r[0])), cv2.INTER_NEAREST)

    re = np.zeros((height, width, 3)) + padding
    offset = np.array((np.array(re.shape[:2]) - np.array(img.shape[:2])) / 2, dtype=np.int32)
    re[offset[0]:offset[0] + img.shape[0], offset[1]:offset[1] + img.shape[1]] = img

    if get_raw:
        return raw, s, re
    else:
        return None, s, re


def normalize(input_image: np.ndarray, mode_01: bool = True) -> np.ndarray:
    return input_image / 255 if mode_01 else (input_image / 127.5) - 1


def load(image,
         width: int = 512,
         height: int = 512,
         get_raw: bool = False,
         mode_01: bool = True,
         bgr: bool = True,
         padding: int = 255):
    if type(image) is not np.ndarray:
        arr = np.asarray(bytearray(image), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
    else:
        img = image

    if img is None:
        return None, None, None
    if bgr:
        img = img[..., ::-1]

    # cv2.imshow('test', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if mode_01 is not None:
        img = normalize(img, mode_01)

    if width is not None or height is not None:
        img = resize(img[..., :3], width=width, height=height, get_raw=get_raw, padding=padding)
        return img
    else:
        return img


def img2ndarray(img, **kwargs):
    return load(image=img, **kwargs)
