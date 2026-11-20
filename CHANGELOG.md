# 更新日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### Python 课英文版
- 26 课全部译成英文（`python/tutorial/en/`）：课文、练习、参考答案、两级提示、判分信息和常见错误说明都是英文；`python3 python/tutorial/en/run.py A01`
- 网页版新增 https://xudaniel.github.io/minicplex/python/en/ ，右上角一键切换中英文（停在同一课）；两个版本的代码和进度分开保存，共用同一份 Pyodide
- 英文版练习由 `make_exercises.py --lang en` 从英文答案生成；CI 对英文版做和中文版同样的检查，发布前在浏览器里把两个版本都跑一遍

### Python 课：卡住时有人帮
- **常见错误自动说明**：答案不对时，判分会多给一句原因（该用 `//` 却用了 `/`、忘了 `return`、差了 1、中英文标点不同、list 和 tuple、顺序不对……）；代码抛异常时也会解释是什么错
- **分级提示**：全部 26 课、每个要写的函数两级提示（先给方向，再给接近代码的写法），`run.py 02 --hint` / `--hint 2`，网页上 💡 提示 按钮；CI 检查每个挖空的函数都有提示
- **🤔 先猜后跑**：A2、A6、A7、第 3、14、16 课各加一道“先猜结果再运行”的题
- 第 10 课新增按显示宽度对齐（`unicodedata.east_asian_width`），第 12 课的选课表中英文混排终于对齐了
- `run.py all` 改为打印进度表（每课一行进度条），`--verbose` 打印全部细节

### Python 课进阶 13～18
- 新增 6 课：读懂报错和调试（第一道“找 bug”练习：五个能跑但答案错的函数）、函数进阶（`*args`、`**kwargs`、拆包、闭包）、装饰器（`@property`、`@dataclass` 的原理，`retry`、`memoize` 与 `lru_cache`）、生成器和迭代器、文件和数据（pathlib、CSV、JSON）、命令行程序和打包（argparse、`python -m`、pyproject、pip、虚拟环境）
- `make_exercises.py` 支持“找 bug”题：答案后加 `# ===` 和注释掉的有 bug 的版本；`run.py all` 在练习文件跑不起来时退出码 2
- Python 课共 26 节；网页版目录新增“进阶”一栏

### 网页版 Python 课
- 新增 https://xudaniel.github.io/minicplex/python/ ：课文、编辑器、自动判分在同一页，Python 在浏览器里运行（Pyodide，放在 Web Worker 里，死循环可以一键停止），不用安装、不用注册，手机上分“课文 / 练习”两个标签
- 写的代码和完成进度自动保存在浏览器里；出错时用中文指出第几行、什么错、常见原因
- Python 运行时随网站一起发布（另有 jsDelivr / unpkg 备用），打不开 CDN 的地方也能用
- `python/tutorial/make_web.py` 从同一套课文和练习生成；新增 `.github/workflows/pages.yml`：每次先在无头 Chromium 里跑完每一课的答案和练习（`web/test_site.py`），通过才发布

### Python 版
- 新增 `python/`：整个求解器逐行移植到纯 Python（3.9+，只用标准库）——单纯形内核、预处理、Gomory 割、可靠性分支、LP 读写、命令行 `python -m minicplex`（含 `--trace`、`--duals`）、批量求解 `python -m minicplex.bench`（CSV 与 C++ 同格式）、15 个例子（中文注释与 C++ 逐句对应）、20 个 `unittest` 测试
- 建模用运算符重载，写法和 C++ 几乎一样：`m.add_constr(2 * x + 3 * y <= 12, "budget")`；`Params`、`Result` 是 dataclass，`Status` 是 enum
- 一致性：15 个例子输出与导出的 `.lp` 和 C++ 逐字相同；`--trace` 逐行相同；13 个基准模型和 650 道随机题（混合整数、纯 LP、多维背包）的状态、目标值、节点数、迭代次数全部相同
- 逐位一致需要的细节集中在 `python/minicplex/jmath.py`：C++ 式四舍五入（Python 的 `round` 是一半取偶）、保留 `-0.0` 符号且接受无穷大的 `ceil`/`floor`、和 Java 一样的 `min(0.0, -0.0)`、节点队列里 `-0.0` 排在 `0.0` 前面
- 可以 `pip install ./python` 安装（命令 `minicplex-py`）；不安装也能直接运行例子
- 新工具 `tools/compare_examples_py_cpp.sh`；`tools/compare_java_cpp.py` 新增 `--label`；CI 新增 Python 任务（3.9／3.13），每次提交逐题逐步对比

### 用 minicplex 学 Python
- 新增 `python/tutorial/`：20 节中文 Python 课。入门 A1～A8（print 和 f-string、变量、判断、循环、函数、列表、字符串、小项目“挑水果”）；正式课 01～12（模块和 import、小数误差、列表推导式、类、运算符重载和不可变对象、dataclass 和 enum、字典和集合、排序和堆、异常、文本处理、测试、综合项目“选课助手”），例子全部取自 Python 版源代码
- 每课一道自动判分的练习（✅ / ❌ / ⏳）；`python3 python/tutorial/run.py A01` 运行，`run.py` 本身是 Python，Windows 也能直接用；练习由 `make_exercises.py` 从答案挖空生成
- CI 在 Python 3.9 / 3.13 上运行全部参考答案，检查练习和答案同步，并确认挖空的练习只会显示“没写”而不会报错

### Java 零基础入门（A1～A8）
- `java/tutorial/` 新增 8 节零基础小课，每节 10～20 分钟、只学一件事：让程序说话、变量和计算、做判断、重复做事、自己写方法、数组、字符串，最后是小项目“挑水果”（两层循环试遍所有买法，再和 minicplex 求解器对答案）
- 每节一道自动判分的练习和参考答案；`run.sh A01`（或 `A1`）运行，`run.sh all` 包括入门小课；CI 照样运行全部参考答案

### 用 minicplex 学 Java
- 新增 `java/tutorial/`：12 课中文 Java 课（第一个程序、基本类型与小数误差、数组、类、不可变对象、record 与 enum、集合、lambda 与比较器、异常、字符串、包与测试、综合项目“选课助手”），例子全部取自本项目源代码
- 每课一道能自动判分的练习（✅ / ❌ / ⏳），`java/tutorial/run.sh 01` 运行；参考答案在 `solutions/`，练习由 `make_exercises.py` 从答案挖空生成
- CI 在 JDK 17 / 21 上运行全部参考答案，并检查练习和答案同步
- 写教程时发现并修复：`LinExpr.terms()` 直接返回内部 `TreeMap`，外部可以改动“不可变”表达式；现在返回只读视图

### Java 版
- 新增 `java/`：整个求解器逐行移植到 Java 17（零依赖）——单纯形内核、预处理、Gomory 割、可靠性分支、LP 读写、命令行（含 `--trace`）、`Bench`／`Gen` 工具、15 个例子（中文注释与 C++ 逐句对应）、40 项测试
- 构建：`java/build.sh`（只用 javac + jar，不联网）或 `mvn -f java/pom.xml package`
- 一致性：15 个例子输出与导出的 `.lp` 逐字相同；`--trace` 逐行相同；13 个基准模型和 2,000 道随机题的状态、目标值、节点数、迭代次数全部相同
- 新工具 `tools/compare_java_cpp.py`、`tools/compare_examples_java_cpp.sh`；CI 新增 Java 任务（JDK 17／21），每次提交逐题逐步对比

### 确定性修复（移植时发现）
- Gomory 割按效力排序、强分支候选排序改用稳定排序；节点队列在“界、深度”都相同时按插入顺序（新的优先）决定。以前效力完全相同的两个割，选哪个取决于标准库的排序实现，换一个标准库（如 macOS 的 libc++）搜索路径可能不同
- C++ 用 `-ffp-contract=off` 编译：新编译器（如 CI 上默认面向 x86-64-v3 的 GCC 15）或 ARM 上的 Clang 会把 `a*b+c` 合成 FMA 指令，舍入不同导致搜索路径不同（CI 上员工排班 4 个节点，本机 11 个）。现在任何编译器和 CPU 上计算路径都相同
- 对拍脚本：HiGHS 自身出错（返回“其他”状态）时，先关掉 HiGHS 预处理重解，再不行就暴力枚举当裁判。CI 种子 18 的第 311 题就是这样：HiGHS 预处理后内部报错，minicplex 判“不可行”，关预处理的 HiGHS 和暴力枚举都确认不可行
- 影响：员工排班例子节点数 8 → 11（最优值 6,571 不变）；多维背包两个基准模型节点数小幅变化；`bench/baseline.csv` 已更新

### 影子价格与进阶建模
- **对偶值输出**：线性规划求解后提供 `Result::duals`（每条约束的影子价格）和 `Result::reducedCosts`（既约成本），命令行 `--duals`。与 HiGHS 对比 100 道随机 LP 全部一致，单元测试用扰动法核对 235 条约束
- 5 个进阶建模例子 `examples/basics/06～10`：影子价格、固定费用（大 M）、最小化最大值、绝对值、不可行时的弹性约束
- README 新增进阶建模讲解、建模技巧速查表、5 道带答案的练习题

### 整数规划提速（PRD 建议 2）
- **可靠性分支**：按伪成本（每单位变化的目标增量）乘积打分选分支变量；尚无观测的变量先做强分支（两侧各试算 40 步对偶单纯形）初始化，两侧都不可行时直接剪掉节点
- **根节点 Gomory 混合整数割**：从单纯形表直接生成，支持有界变量和整数松弛变量；按效力、平行度、数值跨度过滤；默认 2 轮，只保留紧的割
- **预处理**：边界传播、0-1 变量大 M 系数收紧、删除冗余行、提前判定不可行；不删除变量，无需还原
- 新参数：`Params::branching`、`cutRounds`、`presolve`；命令行 `--branch pc|frac`、`--cuts K`、`--no-presolve`

### 学习辅助
- `--trace`（`Params::trace`）：打印每一次换基（谁进基、谁离基、步长、既约成本）、每一个割平面、每个节点的来源、剪枝原因、启发式解和分支决定
- 5 个入门例子 `examples/basics/01～05`（一个变量 → 两个变量 → 整数 → 0-1 → 最小化），每个只引入一个新概念，中文逐行注释；README 新增入门例子讲解和常见 0-1 规则写法表
- 新例子 `examples/bakery.lp`（面包店整数版），README 代码解析新增调用链时序图、源码摘录、逐步实例、不变式、复杂度和扩展指南

### 效果（18 个整数规划评测集，对比 v1.0.0）
- 节点总数 47,304 → 34,034（减少 28%），总用时快 1.7 倍
- 生产排程例子：7,001 → 419 个节点，0.31 秒 → 0.03 秒
- 较大的随机混合题（200 道）：节点 33.5 万 → 4.1 万

### 修复
- 对拍发现：大量强分支换基后单纯形表有微小漂移，曾接受一个违反约束 3×10⁻⁵ 的伪解（目标 58.8，真实最优 31.9）。现在判定最优前会用原始矩阵复核每一行，并在接受整数解前做“抛光”（固定整数变量、用全新 LP 重解连续部分）

- 写代码解析时用 `--trace` 对拍发现：预处理给连续变量边界留的安全余量（1e-7）会被 LP 利用，再被接受整数解前的预检查（1e-6）误拒，导致一道可行题报“不可行”。余量改为 1e-9，含连续变量时预检查放宽到 1e-4，最终仍由抛光后的 1e-7 严格检查把关
- 新增绝对 MIP 间隙 `Params::mipAbsGap`（默认 1e-6，对应 CPLEX EpAGap），命令行 `--absgap`
- 已知局限：整数变量无界且 LP 界沿射线不变时，分支定界可能无法在节点上限内证明最优（答案通常已是最优）；对拍脚本把这种情况单独统计

### 测试
- 新增与 Google OR-Tools 对拍：`tools/verify_with_ortools.py`、`tools/fuzz_vs_ortools.py`（GLOP／SCIP，不一致时请 HiGHS 裁判，纯 LP 顺带对比迭代次数）。首批 1,030 道随机题（混合整数 1,000、纯 LP 30）全部一致；纯 LP 迭代次数中位数约为 GLOP 的 1.15 倍（GLOP 含预处理，仅作参考）
- 对拍中发现 OR-Tools 的两处行为并已在脚本中处理：MPSolver 把 GLOP 的“不可行或无界”报成“不可行”（500 道题中有 69 道）；LP 松弛无界的整数题，SCIP 会一直搜索
- 新增预处理、Gomory 割有效性（288 个割 × 24,532 个整数点）测试；暴力枚举测试在 3 组参数下运行
- 与 HiGHS 对拍约 4,000 道（混合、较大混合、背包、纯 LP）全部一致

## [1.0.0] - 2026-11-19

第一个正式版本。

### 求解内核
- 有界变量单纯形：每条约束配一个松弛变量（`A x − s = 0`），变量边界不占约束行，无需人工变量
- 原始单纯形：组合式第一阶段（最小化越界量之和）+ 第二阶段，支持 bound flip
- 对偶单纯形：基对偶可行时自动使用；对偶目标达到截断值时提前停止
- 基的保存与增量恢复；定期从原矩阵重建单纯形表，抑制舍入误差
- Dantzig 定价，退化时切换 Bland 规则防止循环

### 混合整数规划
- 分支定界 + 下潜：子节点从父节点的单纯形表热启动
- 兄弟节点保存父节点的基；最优界优先选点；最分数变量分支
- 取整启发式；整数目标函数的界加强；相对间隙、节点上限、时间上限

### 建模与输入输出
- Concert 风格 C++ API：`2 * x + 3 * y <= 12`
- CPLEX LP 格式读取与写出（Minimize/Maximize、Subject To、Bounds、General、Binary、End）
- 命令行：`--relax`、`--gap`、`--nodes`、`--time`、`--quiet`、`--all`、`--write`，类 CPLEX 节点日志

### 例子
- 入门：面包店生产计划（LP）、投资项目选择（0-1）
- 复杂：3 产品 × 6 周生产排程（最低 35,615 元）、餐厅 8 人一周排班（最低 6,571 元）

### 工程质量
- GitHub Actions：Linux / macOS 编译测试、AddressSanitizer + UBSan、与 HiGHS 自动对拍、基准对比
- 工具：随机模型生成器 `minicplex_gen`、批量求解 `minicplex_bench`、`tools/fuzz_vs_highs.py`、`tools/bench_compare.py`

### 性能（bench/ 中 13 个模型，对比早期 v0.1 内核）
- 单纯形迭代：777,609 → 40,804（减少 95%）
- 总用时：2.78 秒 → 约 0.6 秒（本地），CI 机器上快 6.9 倍

### 修复
- 导出 LP 文件时，被固定为 0 的 0-1 变量会丢失边界

### 已知限制
- 稠密单纯形表，适合几百行 / 列规模的模型
- 不支持二次规划、SOS、半连续变量、MPS 文件、范围约束

## [0.1.0] - 2026-11-18

- 初始版本：两阶段稠密单纯形、最优界优先分支定界、CPLEX LP 读写、命令行、单元测试
