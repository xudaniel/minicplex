/*
 * fft.c —— 纯手写 C 的快速傅里叶变换（FFT），并和慢的 DFT 对比
 *
 * 只用 <stdio.h> 打印结果；sin、cos、开方都自己写。
 *
 * 编译：gcc fft.c -o fft
 * 运行：./fft
 */
#include <stdio.h>

#define PI   3.14159265358979323846
#define BIG  4096                   /* 对比速度用的点数（必须是 2 的幂） */

static long g_count;                /* 数一数做了多少次“乘波”运算 */

/* ---------- 自己写的数学函数（代替 <math.h>） ---------- */

static double my_sin(double x) {    /* x 在 [-π, π]，泰勒级数 */
    double term = x, sum = x;
    for (int i = 1; i <= 12; i++) {
        term *= -x * x / ((2 * i) * (2 * i + 1));
        sum += term;
    }
    return sum;
}

static double my_cos(double x) {    /* x 在 [-π, π]，泰勒级数 */
    double term = 1, sum = 1;
    for (int i = 1; i <= 12; i++) {
        term *= -x * x / ((2 * i - 1) * (2 * i));
        sum += term;
    }
    return sum;
}

static double my_sqrt(double v) {   /* 牛顿法 */
    if (v <= 0) return 0;
    double r = v > 1 ? v : 1;
    for (int i = 0; i < 60; i++) r = (r + v / r) / 2;
    return r;
}

static double my_abs(double v) { return v < 0 ? -v : v; }

/* ---------- 慢版：DFT，N 个频率 × N 个点 = N² 次 ---------- */

static void dft(const double x[], double re[], double im[], int n) {
    for (int k = 0; k < n; k++) {
        re[k] = 0;
        im[k] = 0;
        for (int j = 0; j < n; j++) {
            double a = 2 * PI * ((k * j) % n) / n;
            if (a > PI) a -= 2 * PI;
            re[k] += x[j] * my_cos(a);
            im[k] -= x[j] * my_sin(a);
            g_count++;
        }
    }
}

/* ---------- 快版：FFT，分成两半、各自算、再合并 ---------- */

/*
 * re[]、im[] 进来时是信号（实部、虚部），出去时是频谱。n 必须是 2 的幂。
 *
 * 思路：
 *   1. 把 n 个点按位置分成“偶数位”和“奇数位”两组，各 n/2 个
 *   2. 两组各自做一次 FFT（递归，问题小了一半）
 *   3. 合并：X[k]       = 偶[k] + w·奇[k]
 *            X[k + n/2] = 偶[k] − w·奇[k]      w = 转 k/n 圈的那个“标准波”
 *      同一个 w·奇[k] 用了两次，这就是省下一半计算的地方
 */
static void fft(double re[], double im[], int n) {
    if (n == 1) return;             /* 只剩 1 个点：它自己就是答案 */

    int h = n / 2;
    double er[h], ei[h], odr[h], odi[h];

    for (int i = 0; i < h; i++) {   /* 1. 拆成偶数位和奇数位 */
        er[i]  = re[2 * i];      ei[i]  = im[2 * i];
        odr[i] = re[2 * i + 1];  odi[i] = im[2 * i + 1];
    }

    fft(er, ei, h);                 /* 2. 两半各自算 */
    fft(odr, odi, h);

    for (int k = 0; k < h; k++) {   /* 3. 合并 */
        double a  = 2 * PI * k / n;             /* k < n/2，所以 a 在 [0, π) */
        double wr = my_cos(a), wi = -my_sin(a); /* w = cos − i·sin */
        double tr = wr * odr[k] - wi * odi[k];  /* t = w × 奇[k]（复数乘法） */
        double ti = wr * odi[k] + wi * odr[k];
        re[k]     = er[k] + tr;  im[k]     = ei[k] + ti;
        re[k + h] = er[k] - tr;  im[k + h] = ei[k] - ti;
        g_count++;
    }
}

/* ---------- 演示 ---------- */

/* 造信号：频率 f1（振幅 1.0）+ 频率 f2（振幅 0.5） */
static void make_signal(double x[], int n, int f1, int f2) {
    for (int j = 0; j < n; j++) {
        double a1 = 2 * PI * ((f1 * j) % n) / n;
        double a2 = 2 * PI * ((f2 * j) % n) / n;
        if (a1 > PI) a1 -= 2 * PI;
        if (a2 > PI) a2 -= 2 * PI;
        x[j] = 1.0 * my_sin(a1) + 0.5 * my_sin(a2);
    }
}

static double amp(double re, double im, int n) {
    return my_sqrt(re * re + im * im) * 2 / n;
}

int main(void) {
    /* ===== 第一部分：32 个点，两种算法结果并排 ===== */
    enum { N = 32 };
    double x[N], dr[N], di[N], fr[N], fi[N];

    make_signal(x, N, 3, 7);
    dft(x, dr, di, N);
    for (int j = 0; j < N; j++) { fr[j] = x[j]; fi[j] = 0; }
    fft(fr, fi, N);

    printf("32 个点，信号 = 频率 3（振幅 1.0）+ 频率 7（振幅 0.5）\n\n");
    printf("频率   DFT     FFT\n");
    for (int k = 0; k <= 8; k++)
        printf(" %2d   %.3f   %.3f\n", k, amp(dr[k], di[k], N), amp(fr[k], fi[k], N));
    printf(" ...  （9 到 16 都是 0.000）\n");

    /* ===== 第二部分：4096 个点，比谁算得少 ===== */
    static double bx[BIG], bdr[BIG], bdi[BIG], bfr[BIG], bfi[BIG];

    make_signal(bx, BIG, 50, 120);

    g_count = 0;
    dft(bx, bdr, bdi, BIG);
    long c_dft = g_count;

    for (int j = 0; j < BIG; j++) { bfr[j] = bx[j]; bfi[j] = 0; }
    g_count = 0;
    fft(bfr, bfi, BIG);
    long c_fft = g_count;

    double maxdiff = 0;
    for (int k = 0; k < BIG; k++) {
        double d1 = my_abs(bdr[k] - bfr[k]), d2 = my_abs(bdi[k] - bfi[k]);
        if (d1 > maxdiff) maxdiff = d1;
        if (d2 > maxdiff) maxdiff = d2;
    }

    printf("\n%d 个点，信号 = 频率 50（振幅 1.0）+ 频率 120（振幅 0.5）\n\n", BIG);
    printf("FFT 找到的峰：");
    for (int k = 0; k <= BIG / 2; k++) {
        double a = amp(bfr[k], bfi[k], BIG);
        if (a > 0.01) printf("频率 %d 振幅 %.3f   ", k, a);
    }
    printf("\n\n运算次数：\n");
    printf("  DFT：%10ld 次  （N × N）\n", c_dft);
    printf("  FFT：%10ld 次  （N/2 × log2 N）\n", c_fft);
    printf("  FFT 少算 %ld 倍\n", c_dft / c_fft);
    printf("\n两种算法结果的最大差距：%.2e（只是小数点后十几位的舍入误差）\n", maxdiff);

    return 0;
}
