package minicplex.tutorial;

/**
 * 入门 A1：让程序说话。
 *
 * <p>只需要改每个方法大括号里的那一行。“方法”是什么，A5 再讲。
 * 运行：java/tutorial/run.sh A01
 */
public class A01Hello {

    /** 返回一句固定的话：Hello, Java! */
    static String hello() {
        // TODO 把下面这一行换成：return "Hello, Java!";
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 跟人打招呼：greet("小明") 返回 "你好，小明！" */
    static String greet(String name) {
        // TODO 用 + 把三段拼起来："你好，" + name + "！"
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 报价：price("苹果", 2) 返回 "苹果：2 元"。数字和文字也能用 + 拼在一起。 */
    static String price(String item, int yuan) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("入门 A1：让程序说话");
        System.out.println("（这一行是 main 自己打印的：程序从 main 开始运行）");
        Check.eq("hello() 返回 Hello, Java!", "Hello, Java!", () -> hello());
        Check.eq("greet(\"小明\")", "你好，小明！", () -> greet("小明"));
        Check.eq("greet(\"Mia\")", "你好，Mia！", () -> greet("Mia"));
        Check.eq("price(\"苹果\", 2)", "苹果：2 元", () -> price("苹果", 2));
        Check.eq("price(\"香蕉\", 1)", "香蕉：1 元", () -> price("香蕉", 1));
        Check.done();
    }
}
