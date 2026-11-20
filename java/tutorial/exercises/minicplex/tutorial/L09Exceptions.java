package minicplex.tutorial;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import minicplex.*;

/**
 * 第 9 课练习：异常。
 *
 * <p>运行：java/tutorial/run.sh 09
 */
public class L09Exceptions {

    /** 把字符串转成小数；转不了就返回 fallback。Double.parseDouble 失败时抛 NumberFormatException。 */
    static double parseOr(String s, double fallback) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 用 LpReader 读一段 LP 文本。读成功返回 0；读失败时，错误信息里有 "line 数字"，把这个行号找出来返回。
     */
    static int errorLine(String lpText) {
        // TODO try { LpReader.readString(lpText); return 0; } catch (RuntimeException e) { ... e.getMessage() ... }
        //      用正则 "line (\\d+)" 取出数字
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 读文件第一行。用 try-with-resources 保证文件一定会被关闭；
     * IOException 是受检异常，把它包成 UncheckedIOException 再抛出去（LpReader.readFile 也是这样包装的）。
     */
    static String firstLine(Path path) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) throws IOException {
        Check.lesson("第 9 课：异常");
        Check.near("\"3.5\" 转成 3.5", 3.5, () -> parseOr("3.5", -1));
        Check.near("\"abc\" 转不了，返回默认值", -1, () -> parseOr("abc", -1));
        Check.eq("正确的模型返回 0", 0, () -> errorLine("Minimize\n obj: x\nSubject To\n c: x >= 1\nEnd\n"));
        Check.eq("第 2 行多了个加号，错误在第 3 行被发现", 3, () -> errorLine("Minimize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n"));
        Check.throwsA("变量名重复时，Model.addVar 抛 IllegalArgumentException", IllegalArgumentException.class, () -> {
            Model m = new Model();
            m.addVar(0, 1, VarType.BINARY, "x");
            m.addVar(0, 1, VarType.BINARY, "x");
        });
        Path tmp = Files.createTempFile("minicplex", ".txt");
        Files.writeString(tmp, "第一行\n第二行\n", StandardCharsets.UTF_8);
        Check.eq("读到第一行", "第一行", () -> firstLine(tmp));
        Files.delete(tmp);
        Check.throwsA("文件不存在时抛 UncheckedIOException", UncheckedIOException.class,
                () -> firstLine(Path.of("no-such-file.txt")));
        Check.done();
    }
}
