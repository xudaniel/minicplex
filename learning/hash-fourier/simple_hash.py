def fnv1a(text):
    h = 2166136261                      # 起点：一个固定的数
    for b in text.encode("utf-8"):      # 先把文字变成字节
        h ^= b                          # 1. 把一个字节混进去
        h = (h * 16777619) & 0xFFFFFFFF # 2. 乘质数搅散，只留 32 位
    return f"{h:08x}"

print(fnv1a("我的一句话"))    # 21838ace
print(fnv1a("我的一句话。"))  # 5656f755
