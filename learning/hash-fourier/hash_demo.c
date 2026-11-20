/*
 * hash_demo.c —— 纯手写 C 的 SHA-256，给一句话算 hash
 *
 * 除了 <stdio.h>（只用来在屏幕上打字、从键盘读字），
 * 其余全部自己写：数据类型、字符串长度、复制、比较、拼接、SHA-256 本身。
 *
 * 编译：gcc hash_demo.c -o hash_demo
 * 用法：./hash_demo "你的一句话"
 *       ./hash_demo --trace "你的一句话"   逐轮追踪：句尾加一个句号，
 *                                         看差别怎么在 64 轮里扩散开
 *       不带参数时，会让你在终端里输入一句话
 */
#include <stdio.h>   /* 唯一的头文件：printf、fgets 负责输入输出 */

/* ---------- 自己定义的数据类型（代替 <stdint.h>） ---------- */

typedef unsigned char      u8;    /* 1 字节 */
typedef unsigned int       u32;   /* 4 字节 */
typedef unsigned long long u64;   /* 8 字节 */

/* 编译时检查：如果 u32 不是 4 字节、u64 不是 8 字节，数组长度变成 -1，直接编译失败 */
typedef char check_u32_is_4_bytes[sizeof(u32) == 4 ? 1 : -1];
typedef char check_u64_is_8_bytes[sizeof(u64) == 8 ? 1 : -1];

/* ---------- 自己写的字符串和内存工具（代替 <string.h>） ---------- */

static unsigned long my_strlen(const char *s) {
    unsigned long n = 0;
    while (s[n] != '\0') n++;
    return n;
}

static int my_strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (u8)*a - (u8)*b;
}

static void my_memcpy(void *dst, const void *src, unsigned long n) {
    u8 *d = (u8 *)dst;
    const u8 *s = (const u8 *)src;
    while (n--) *d++ = *s++;
}

static void my_memset(void *dst, u8 v, unsigned long n) {
    u8 *d = (u8 *)dst;
    while (n--) *d++ = v;
}

static int my_memeq(const void *a, const void *b, unsigned long n) {
    const u8 *x = (const u8 *)a, *y = (const u8 *)b;
    while (n--) if (*x++ != *y++) return 0;
    return 1;
}

/* 把 a 和 b 拼到 out 里，最多写 cap-1 个字节 */
static void my_concat(char *out, unsigned long cap, const char *a, const char *b) {
    unsigned long i = 0;
    while (*a && i + 1 < cap) out[i++] = *a++;
    while (*b && i + 1 < cap) out[i++] = *b++;
    out[i] = '\0';
}

/* 去掉字符串末尾的回车 */
static void chomp(char *s) {
    for (; *s; s++)
        if (*s == '\n' || *s == '\r') { *s = '\0'; return; }
}

/* ---------- SHA-256 实现 ---------- */

typedef struct {
    u8  data[64];    /* 当前还没处理的 64 字节块 */
    u32 datalen;     /* data 里已有多少字节 */
    u64 bitlen;      /* 已处理的总位数 */
    u32 state[8];    /* 8 个 32 位的中间结果 */
} SHA256_CTX;

/* 64 个常数：前 64 个质数立方根的小数部分 */
static const u32 K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

#define ROTR(x,n)  (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x,y,z)  (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x)     (ROTR(x,2)  ^ ROTR(x,13) ^ ROTR(x,22))
#define EP1(x)     (ROTR(x,6)  ^ ROTR(x,11) ^ ROTR(x,25))
#define SIG0(x)    (ROTR(x,7)  ^ ROTR(x,18) ^ ((x) >> 3))
#define SIG1(x)    (ROTR(x,17) ^ ROTR(x,19) ^ ((x) >> 10))

/* ---------- 追踪：记下每一轮 a..h 的值（--trace 用） ---------- */
#define MAX_BLOCKS 20
typedef struct {
    int on;                       /* 1 = 开启记录 */
    int blocks;                   /* 已记录了几块 */
    u32 r[MAX_BLOCKS][65][8];     /* r[块][0] = 开始前，r[块][i+1] = 第 i 轮后 */
    u32 m[MAX_BLOCKS][64];        /* 每块展开后的 64 个消息字 */
    u32 out[MAX_BLOCKS][8];       /* 每块“加回去”之后的 state */
} Trace;
static Trace *g_trace = 0;

/* 处理一个 64 字节的块：把数据反复搅拌 64 轮 */
static void sha256_transform(SHA256_CTX *ctx, const u8 data[64]) {
    u32 a, b, c, d, e, f, g, h, t1, t2, m[64];
    int i;

    /* 展开：64 字节 → 16 个 32 位数（大端序），再推出另外 48 个 */
    for (i = 0; i < 16; i++)
        m[i] = ((u32)data[i*4] << 24) | ((u32)data[i*4+1] << 16)
             | ((u32)data[i*4+2] << 8) | ((u32)data[i*4+3]);
    for (; i < 64; i++)
        m[i] = SIG1(m[i-2]) + m[i-7] + SIG0(m[i-15]) + m[i-16];

    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    int blk = -1;
    if (g_trace && g_trace->on && g_trace->blocks < MAX_BLOCKS) {
        blk = g_trace->blocks++;
        my_memcpy(g_trace->m[blk], m, sizeof m);
        u32 s0[8] = {a,b,c,d,e,f,g,h};
        my_memcpy(g_trace->r[blk][0], s0, sizeof s0);
    }

    /* 64 轮压缩 */
    for (i = 0; i < 64; i++) {
        t1 = h + EP1(e) + CH(e,f,g) + K[i] + m[i];
        t2 = EP0(a) + MAJ(a,b,c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;

        if (blk >= 0) {
            u32 s[8] = {a,b,c,d,e,f,g,h};
            my_memcpy(g_trace->r[blk][i + 1], s, sizeof s);
        }
    }

    /* 加回去：让过程没法倒推 */
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;

    if (blk >= 0) my_memcpy(g_trace->out[blk], ctx->state, sizeof ctx->state);
}

static void sha256_init(SHA256_CTX *ctx) {
    ctx->datalen = 0;
    ctx->bitlen  = 0;
    /* 初始值：前 8 个质数平方根的小数部分 */
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
}

static void sha256_update(SHA256_CTX *ctx, const u8 *data, unsigned long len) {
    for (unsigned long i = 0; i < len; i++) {
        ctx->data[ctx->datalen++] = data[i];
        if (ctx->datalen == 64) {
            sha256_transform(ctx, ctx->data);
            ctx->bitlen += 512;
            ctx->datalen = 0;
        }
    }
}

static void sha256_final(SHA256_CTX *ctx, u8 hash[32]) {
    u32 i = ctx->datalen;

    /* 补位：先加一个 1，再补 0，最后 8 字节写总长度 */
    ctx->data[i++] = 0x80;
    if (ctx->datalen >= 56) {
        while (i < 64) ctx->data[i++] = 0x00;
        sha256_transform(ctx, ctx->data);
        i = 0;
    }
    while (i < 56) ctx->data[i++] = 0x00;

    ctx->bitlen += (u64)ctx->datalen * 8;
    for (int j = 0; j < 8; j++)
        ctx->data[63 - j] = (u8)(ctx->bitlen >> (j * 8));
    sha256_transform(ctx, ctx->data);

    for (int j = 0; j < 8; j++) {
        hash[j*4]     = (u8)(ctx->state[j] >> 24);
        hash[j*4 + 1] = (u8)(ctx->state[j] >> 16);
        hash[j*4 + 2] = (u8)(ctx->state[j] >> 8);
        hash[j*4 + 3] = (u8)(ctx->state[j]);
    }
}

/* ---------- 小工具 ---------- */

static void sha256_string(const char *s, u8 out[32]) {
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, (const u8 *)s, my_strlen(s));
    sha256_final(&ctx, out);
}

static void print_hex(const u8 h[32]) {
    for (int i = 0; i < 32; i++) printf("%02x", h[i]);
    printf("\n");
}

/* 数一个 32 位数里有几个 1 */
static int pop32(u32 x) {
    int n = 0;
    while (x) { n += x & 1; x >>= 1; }
    return n;
}

/* 两个 hash 有多少位不同 */
static int diff_bits(const u8 a[32], const u8 b[32]) {
    int n = 0;
    for (int i = 0; i < 32; i++) n += pop32((u32)(a[i] ^ b[i]));
    return n;
}

/* 两组 8 个数（共 256 位）里有多少位不同 */
static int diff8(const u32 a[8], const u32 b[8]) {
    int n = 0;
    for (int i = 0; i < 8; i++) n += pop32(a[i] ^ b[i]);
    return n;
}

static void print_bar(int bits) {
    /* 每 8 位画一格，满 256 位 = 32 格 */
    int cells = (bits + 7) / 8;
    for (int i = 0; i < cells; i++) printf("█");
}

static void print_state(const char *label, const u32 s[8]) {
    printf("  %s", label);
    for (int i = 0; i < 8; i++) printf(" %08x", s[i]);
    printf("\n");
}

/* 逐轮对比两句话：看差别从哪一轮进来、怎么扩散 */
static void trace_compare(const char *s1, const char *s2) {
    static Trace t1, t2;           /* 比较大，放静态区 */
    u8 h[32];

    my_memset(&t1, 0, sizeof t1); t1.on = 1;
    g_trace = &t1; sha256_string(s1, h);
    my_memset(&t2, 0, sizeof t2); t2.on = 1;
    g_trace = &t2; sha256_string(s2, h);
    g_trace = 0;

    int nb = t1.blocks < t2.blocks ? t1.blocks : t2.blocks;
    printf("\n========== 逐轮追踪 ==========\n");
    printf("原句 %lu 字节 → %d 块；新句 %lu 字节 → %d 块（每块 64 字节）\n",
           my_strlen(s1), t1.blocks, my_strlen(s2), t2.blocks);

    for (int b = 0; b < nb; b++) {
        if (diff8(t1.r[b][0], t2.r[b][0]) == 0 &&
            my_memeq(t1.m[b], t2.m[b], sizeof t1.m[b]))
            continue;              /* 这一块两边完全一样，跳过 */

        printf("\n--- 第 %d 块 ---\n", b + 1);

        printf("消息字 m[i] 里不同的位置：");
        int first = -1;
        for (int i = 0; i < 16; i++)
            if (t1.m[b][i] != t2.m[b][i]) {
                printf("m[%d] ", i);
                if (first < 0) first = i;
            }
        printf("（原始 16 个）\n");
        if (first > 0)
            printf("→ 第 0 到 %d 轮用的数据两边一样，差别从第 %d 轮才进来\n",
                   first - 1, first);

        printf("\n 轮   a..h 不同位数（满 256，随机约 128）\n");
        for (int i = 0; i <= 64; i++) {
            int d = diff8(t1.r[b][i], t2.r[b][i]);
            if (i == 0) printf(" 开始 %3d  ", d);
            else        printf(" %3d  %3d  ", i - 1, d);
            print_bar(d);
            printf("\n");
        }
        int dout = diff8(t1.out[b], t2.out[b]);
        printf(" 加回 %3d  ", dout);
        print_bar(dout);
        printf("\n");

        /* 挑几个关键轮次，把 a..h 原值打出来对照 */
        int picks[] = { first, first + 1, first + 4, 64 };
        printf("\n关键轮次的 a b c d e f g h（上行原句，下行新句）：\n");
        for (int k = 0; k < 4; k++) {
            int i = picks[k];
            if (i < 0 || i > 64) continue;
            if (i == 64) printf("第 63 轮后（最后）：\n");
            else         printf("第 %d 轮后：\n", i);
            int idx = (i == 64) ? 64 : i + 1;
            print_state("原", t1.r[b][idx]);
            print_state("新", t2.r[b][idx]);
        }
    }
}

int main(int argc, char *argv[]) {
    char line[1024];
    const char *msg;
    int trace = 0;

    if (argc > 1 && my_strcmp(argv[1], "--trace") == 0) {
        trace = 1;
        argc--; argv++;
    }

    if (argc > 1) {
        msg = argv[1];
    } else {
        printf("输入一句话：");
        if (!fgets(line, sizeof line, stdin)) return 1;
        chomp(line);
        msg = line;
    }

    u8 h1[32], h2[32];
    sha256_string(msg, h1);

    printf("原句：%s\n", msg);
    printf("SHA-256：");
    print_hex(h1);

    /* 雪崩效应演示：只在句尾加一个句号，看 hash 变了多少 */
    char changed[1100];
    my_concat(changed, sizeof changed, msg, "。");
    sha256_string(changed, h2);

    printf("\n句尾加一个“。”：%s\n", changed);
    printf("SHA-256：");
    print_hex(h2);
    printf("\n256 位里有 %d 位不同（随机的话约 128 位）\n", diff_bits(h1, h2));

    if (trace) trace_compare(msg, changed);

    return 0;
}
