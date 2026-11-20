/*
 * fourier.c —— 纯手写 C 的傅里叶变换（DFT，离散傅里叶变换）
 *
 * 只用 <stdio.h> 打印结果；sin、cos、开方都自己写。
 *
 * 编译：gcc fourier.c -o fourier
 * 运行：./fourier
 */
#include <stdio.h>

#define N  32                       /* 采样点数 */
#define PI 3.14159265358979323846

/* ---------- 自己写的数学函数（代替 <math.h>） ---------- */

/* sin(x)，x 在 [-π, π]：泰勒级数 x - x³/3! + x⁵/5! - ... */
static double my_sin(double x) {
    double term = x, sum = x;
    for (int i = 1; i <= 12; i++) {
        term *= -x * x / ((2 * i) * (2 * i + 1));
        sum += term;
    }
    return sum;
}

/* cos(x)，x 在 [-π, π]：泰勒级数 1 - x²/2! + x⁴/4! - ... */
static double my_cos(double x) {
    double term = 1, sum = 1;
    for (int i = 1; i <= 12; i++) {
        term *= -x * x / ((2 * i - 1) * (2 * i));
        sum += term;
    }
    return sum;
}

/* 开平方：牛顿法，反复取平均 */
static double my_sqrt(double v) {
    if (v <= 0) return 0;
    double r = v > 1 ? v : 1;
    for (int i = 0; i < 60; i++) r = (r + v / r) / 2;
    return r;
}

/* ---------- 傅里叶变换 ---------- */

/*
 * X[k] = Σ x[n] · (cos(2πkn/N) − i·sin(2πkn/N))
 *
 * 意思：拿一个每 N 个点转 k 圈的“标准波”去和信号逐点相乘再求和。
 * 信号里有这个频率，乘积就会累加成一个大数；没有，就正负抵消成 0。
 */
static void dft(const double x[N], double re[N], double im[N]) {
    for (int k = 0; k < N; k++) {           /* 对每一个频率 k */
        re[k] = 0;
        im[k] = 0;
        for (int n = 0; n < N; n++) {       /* 把所有采样点过一遍 */
            /* 角度 2πkn/N：先用取余把它收进一圈，再挪到 [-π, π] */
            double a = 2 * PI * ((k * n) % N) / N;
            if (a > PI) a -= 2 * PI;
            re[k] += x[n] * my_cos(a);      /* 和 cos 波的相似度 */
            im[k] -= x[n] * my_sin(a);      /* 和 sin 波的相似度 */
        }
    }
}

int main(void) {
    double x[N], re[N], im[N];

    /* 造一个信号：频率 3（振幅 1.0）+ 频率 7（振幅 0.5）混在一起 */
    for (int n = 0; n < N; n++) {
        double a3 = 2 * PI * ((3 * n) % N) / N;
        double a7 = 2 * PI * ((7 * n) % N) / N;
        if (a3 > PI) a3 -= 2 * PI;
        if (a7 > PI) a7 -= 2 * PI;
        x[n] = 1.0 * my_sin(a3) + 0.5 * my_sin(a7);
    }

    printf("输入信号（%d 个采样点，看不出里面有什么频率）：\n", N);
    for (int n = 0; n < N; n++) {
        printf("%6.2f ", x[n]);
        if (n % 8 == 7) printf("\n");
    }

    dft(x, re, im);

    printf("\n傅里叶变换后（每个频率的振幅）：\n");
    printf("频率  振幅\n");
    for (int k = 0; k <= N / 2; k++) {
        /* 振幅 = |X[k]| × 2/N */
        double amp = my_sqrt(re[k] * re[k] + im[k] * im[k]) * 2 / N;
        printf(" %2d   %.3f  ", k, amp);
        for (int i = 0; i < (int)(amp * 30 + 0.5); i++) printf("█");
        printf("\n");
    }
    return 0;
}
