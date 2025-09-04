import random
import string

def generate_1kb_data():
    """
    生成大约1KB（1024字节）大小的随机字符串数据，并作为返回值返回
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=1024))

# 示例：直接获取1KB数据
if __name__ == "__main__":
    data = generate_1kb_data()
    print(f"生成的数据长度: {len(data)} 字符")
    print(data)

