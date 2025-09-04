import random
import string

def generate_1kb_data():
    """
    生成大约1KB（1024字节）大小的随机字符串数据，并作为返回值返回
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=1024))

def generate_200b_data():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=200))

def generate_150b_data():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=150))