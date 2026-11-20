#include <stdio.h>

/* FNV-1a：最简单的 hash 之一 */
unsigned int hash(const char *s) {
    unsigned int h = 2166136261u;      /* 起点：一个固定的数 */
    while (*s) {
        h ^= (unsigned char)*s++;      /* 1. 把一个字节混进去 */
        h *= 16777619u;                /* 2. 乘一个质数，把它搅散 */
    }
    return h;
}

int main(void) {
    printf("%08x\n", hash("我的一句话"));
    printf("%08x\n", hash("我的一句话。"));
    return 0;
}
