# walkthrough.py —— 跟着一张纸条走一趟：把五站的输入、输出和中间过程全部打印出来
# Follow one note through the five stations, printing every input, output and check.
# 逻辑全在同目录的 staffing_agent.py，这里只负责「边跑边讲」 / all logic lives in staffing_agent.py
# 用法 / Usage（加 --lang en 换成英文 / add --lang en for English）:
#   python3 walkthrough.py                  主角那句话 / the main sentence
#   python3 walkthrough.py --all            主角 + 三个翻车现场 + 四道考考你 / plus three failures and four quiz questions
#   python3 walkthrough.py -i               交互，空行退出 / interactive; empty line quits
#   python3 walkthrough.py "需求改成 1300 次" [--yes]
import sys, re, json
import staffing_agent as A

W = {  # 中文, English
 "s0": ("第 0 站｜墙上的规矩", "Station 0 | The rules on the wall"),
 "row": ("  {k:<5} 每班 {n:>2} 次  每班 {c:>2}  最多 {cap:>2} 班  → 每次 {u:g}",
         "  {k:<17} {n:>2} visits/shift  cost {c:>2}/shift  max {cap:>2}  → {u:g} per visit"),
 "wall1": ("  平时需求 {d} 次；合同规则：派遣用满才能叫加急 = {r}",
           "  Usual demand {d} visits; contract rule (fill dispatch before rush) = {r}"),
 "wall2": ("  门卫规矩：需求 {lo}–{hi} 次，价格变动 ±{p}%；审批线 {a}",
           "  Guard rules: demand {lo}–{hi}, price change ±{p}%; approval line {a}"),
 "s1": ("第 1 站｜助理 parse：一句话 → 纸条", "Station 1 | Assistant parse: sentence → note"),
 "in": ("  进：「{t}」", "  In: “{t}”"),
 "none": ("  四张填空模板都没套上 → 交出空纸条", "  None of the four templates fits → hands over an empty note"),
 "tpl": ({"demand": "需求 ___ 次", "cap": "___班 最多 ___ 班", "cost": "___班 改价"},
         {"demand": "demand ___ visits", "cap": "___ at most ___ shifts", "cost": "___ new price"}),
 "fit": ("  套上「{p}」 → 收据「{q}」", "  Fits “{p}” → receipt “{q}”"),
 "out": ("  出：", "  Out: "),
 "s1skip": ("第 1 站｜跳过：测试按钮 changes= 直接塞纸条", "Station 1 | Skipped: test switch changes= hands in a note directly"),
 "s2": ("第 2 站｜门卫 guard：能不能放行", "Station 2 | Gatekeeper guard: may it pass?"),
 "note": ("  纸条 {r} → {v}", "  Note: {r} → {v}"),
 "demandname": ("需求", "demand"),
 "qs": ("    {a} 1 真是你说的吗   {b} 2 只提到一种班   {c} 3 数字合理   {d} 4 不用本人签字",
        "    {a} 1 you really said it   {b} 2 one shift type   {c} 3 number in range   {d} 4 no sign-off needed"),
 "says": ("  门卫说：", "  Gatekeeper: "),
 "verdict": ("  出：{s}  （ok 放行／ask 反问／reject 拒绝／confirm 要确认）",
             "  Out: {s}  (ok pass / ask clarify / reject / confirm needs a person)"),
 "stop": ("\n  🔴 急停：门卫没放行，会计不开工。", "\n  🔴 Emergency stop: the gatekeeper said no, so the accountant never starts."),
 "again": ("带 confirmed=True 再跑一次。", " Run again with confirmed=True."),
 "s3": ("第 3 站｜会计 solve：出题、交给求解器", "Station 3 | Accountant solve: write the model, hand it to the solver"),
 "override": ("  ⚠ 测试按钮：题目被改成 {o}", "  ⚠ Test switch: the model was changed to {o}"),
 "copy": ("  复印件：需求 {d}，上限 {caps}；BASE 原件仍是需求 {bd}、常勤 {bc}（没被改）",
          "  Copy: demand {d}, caps {caps}; the BASE original is still demand {bd}, regular {bc} (untouched)"),
 "solver": ("  求解器 SCIP 给出：", "  SCIP solver returns: "),
 "visits": ("  核对次数：{e} = {tot:g}，缺口 {s:g}，需求 {d}", "  Check visits: {e} = {tot:g}, shortage {s:g}, demand {d}"),
 "cost": ("  核对费用：{e} = {c:g}（平时 {b:g}）", "  Check cost: {e} = {c:g} (usual {b:g})"),
 "s4": ("第 4 站｜老师傅 sanity：怪不怪、谁签字", "Station 4 | Experienced colleague sanity: anything odd? who signs?"),
 "flags": ("  黄灯：", "  Yellow flags: "), "noflag": ("没有", "none"),
 "who": ("  多花 {c:g} − {b:g} = {d:g}，审批线 {a} → {w}", "  Extra cost {c:g} − {b:g} = {d:g}, approval line {a} → {w}"),
 "s5": ("第 5 站｜秘书 explain：说成人话", "Station 5 | Secretary explain: say it in plain words"),
 "confirmed": ("（已确认）", " (confirmed)"),
 "fails": ("\n\n########## 三个翻车现场 ##########", "\n\n########## Three failures ##########"),
 "quiz": ("\n\n########## 考考你 ##########", "\n\n########## Check your understanding ##########"),
 "q2": ("考考你 2｜不复印，直接改 BASE 会怎样", "Quiz 2 | What if we edit BASE instead of a copy?"),
 "q2a": ("  第一句话之后，「平时」变成 {c:g}（本该是 606）", "  After the first sentence, “usual” becomes {c:g} (it should be 606)"),
 "q2b": ("  恢复原件后，「平时」又是 {c:g}", "  After restoring the original, “usual” is {c:g} again"),
 "q3": ("考考你 3｜罚金改成 1", "Quiz 3 | Shortage penalty of 1"),
 "q3a": ("  方案 {p}，缺 {s:g} 次 → 什么都不排（最便宜的补法每次也要 4，比罚 1 贵）",
         "  Plan {p}, short {s:g} → schedules nothing (the cheapest cover costs 4 per visit, more than a penalty of 1)"),
 "ask": ("\n护士长说（空行退出）：", "\nHead nurse says (empty line quits): "),
 "askyes": ("要确认的改动算不算？(y/N) ", "Treat changes needing confirmation as confirmed? (y/N) "),
 "logged": ("\n📒 {n} 张纸条已记进 walkthrough_log.json", "\n📒 {n} note(s) written to walkthrough_log.json"),
}
SENT = {  # 演示用的句子 / demo sentences
 "zh": {"main": "下周三有人请假，常勤最多只能加 4 班", "wrong": "派遣公司说加急每班 40", "big": "需求改成 1300 次",
        "rush40": "派遣公司说加急每班 40", "q1": "派遣最多只能 10 班", "q4": "常勤最多只能加 4 班，需求到 140 次"},
 "en": {"main": "Someone is off next Wednesday, so regular staff can do at most 4 extra shifts",
        "wrong": "The dispatch agency says rush shifts are 40 per shift", "big": "Change demand to 1300 visits",
        "rush40": "The dispatch agency says rush shifts are 40 per shift", "q1": "Dispatch can do at most 10 shifts",
        "q4": "Regular staff can do at most 4 extra shifts, and demand will reach 140 visits"},
}
WRONG_QUOTE = {"zh": "派遣公司说加急每班 40", "en": "The dispatch agency says rush shifts are 40"}

def w(key, **kw):
    v = W[key][A.LANG == "en"]
    return v.format(**kw) if isinstance(v, str) else v
def hr(title): print(f"\n{'─' * 6} {title} {'─' * 6}")
def ok(b): return "✓" if b else "✗"
def z(v): return 0 if abs(v) < 1e-9 else v      # 把 -0 显示成 0 / show -0 as 0
def plan_str(p): return A.t("sep").join(A.t("item", n=A.show(k), v=v, s="" if v == 1 else "s") for k, v in p.items())

def station0():
    hr(w("s0"))
    for k, (n, c, cap) in A.BASE["resources"].items():
        print(w("row", k=A.show(k), n=n, c=c, cap=cap, u=c / n))
    print(w("wall1", d=A.BASE["demand"], r=A.BASE["rush_rule"]))
    lo, hi = A.LIMITS["demand"]
    print(w("wall2", lo=lo, hi=hi, p=A.LIMITS["cost_pct"], a=A.APPROVAL_LINE))

def readable(ch): return json.dumps([{k: A.show(v) if k == "resource" else v for k, v in c.items()} for c in ch], ensure_ascii=False)

def station1(text):
    hr(w("s1")); print(w("in", t=text))
    ch = A.parse(text)
    if not ch: print(w("none"))
    for c in ch: print(w("fit", p=w("tpl")[c["type"]], q=c["quote"]))
    print(w("out") + readable(ch))
    return ch

def station2(text, ch):
    hr(w("s2"))
    for c in ch:
        names = {A.NAMES[k.lower()] for k in re.findall(A.SHIFT, c["quote"], re.I)}
        q1, q2, q3, q4 = c["quote"] in text, len(names) <= 1, True, True
        if c["type"] == "demand": q3 = A.LIMITS["demand"][0] <= c["value"] <= A.LIMITS["demand"][1]
        if c["type"] == "cap": q3 = 0 <= c["value"] <= A.LIMITS["cap"][c["resource"]]
        if c["type"] == "cost":
            b = A.BASE["resources"][c["resource"]][1]; q4 = abs((c["value"] - b) / b * 100) <= A.LIMITS["cost_pct"]
        print(w("note", r=A.show(c["resource"]) if "resource" in c else w("demandname"), v=c["value"]))
        print(w("qs", a=ok(q1), b=ok(q2), c=ok(q3), d=ok(q4)))
    status, notes = A.guard(text, ch)
    for n in notes: print(w("says") + n)
    print(w("verdict", s=status))
    return status

def station3(ch, override):
    hr(w("s3"))
    m = A.apply(ch)
    if override: m.update(override); print(w("override", o=override))
    caps = A.t("sep").join(f"{A.show(k)} {v[2]}" for k, v in m["resources"].items())
    print(w("copy", d=m["demand"], caps=caps, bd=A.BASE["demand"], bc=A.BASE["resources"]["常勤加排"][2]))
    r, base = A.solve(m), A.solve(A.BASE)
    R, p = m["resources"], {k: z(v) for k, v in r["plan"].items()}
    print(w("solver") + plan_str(p))
    e = " + ".join(f"{R[k][0]}×{p[k]:g}" for k in R)
    print(w("visits", e=e, tot=sum(R[k][0] * p[k] for k in R), s=z(r["short"]), d=m["demand"]))
    e = " + ".join(f"{R[k][1]:g}×{p[k]:g}" for k in R)
    print(w("cost", e=e, c=r["cost"], b=base["cost"]))
    return m, r, base

def station4(m, r, base):
    hr(w("s4"))
    flags, who = A.sanity(m, r), A.approver(r, base)
    print(w("flags") + ("" if flags else w("noflag")))
    for f in flags: print("    ⚠ " + f)
    print(w("who", c=r["cost"], b=base["cost"], d=r["cost"] - base["cost"], a=A.APPROVAL_LINE, w=who))
    return flags, who

def station5(r, base, flags, who):
    hr(w("s5")); print("  " + A.explain(r, base, flags, who))

def trip(text, confirmed=False, override=None, changes=None, show_wall=True):
    print(f"\n{'═' * 40}\n" + A.t("say", t=text) + (w("confirmed") if confirmed else ""))
    if show_wall: station0()
    if changes is None: ch = station1(text)
    else: ch = changes; hr(w("s1skip")); print("  " + readable(ch))
    status = station2(text, ch)
    log = {"text": text, "changes": ch, "guard": status}
    if status in ("ask", "reject") or (status == "confirm" and not confirmed):
        print(w("stop") + (w("again") if status == "confirm" else "")); return log
    m, r, base = station3(ch, override)
    flags, who = station4(m, r, base)
    station5(r, base, flags, who)
    log.update(result=r, flags=flags, approver=who); return log

def quiz_no_copy():
    hr(w("q2"))
    saved = json.loads(json.dumps(A.BASE))
    A.BASE["resources"]["常勤加排"][2] = 4           # 模拟「直接在原件上改」 / simulate editing the original
    print(w("q2a", c=A.solve(A.BASE)["cost"]))
    A.BASE.clear(); A.BASE.update(saved)
    print(w("q2b", c=A.solve(A.BASE)["cost"]))

def quiz_penalty():
    hr(w("q3"))
    m = json.loads(json.dumps(A.BASE)); m["shortage_penalty"] = 1
    r = A.solve(m)
    print(w("q3a", p=plan_str(r["plan"]), s=r["short"]))

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--lang" in args:
        i = args.index("--lang"); A.LANG = args[i + 1]; del args[i:i + 2]
    S, logs = SENT[A.LANG], []
    if not args:
        logs.append(trip(S["main"]))
    elif args[0] == "--all":
        logs.append(trip(S["main"]))
        print(w("fails"))
        logs.append(trip(S["wrong"], show_wall=False,
                         changes=[{"type": "cost", "resource": "派遣", "value": 40, "quote": WRONG_QUOTE[A.LANG]}]))
        logs.append(trip(S["big"], show_wall=False))
        logs.append(trip(S["rush40"], confirmed=True, override={"rush_rule": False}, show_wall=False))
        print(w("quiz"))
        logs.append(trip(S["q1"], show_wall=False))
        quiz_no_copy(); quiz_penalty()
        logs.append(trip(S["q4"], show_wall=False))
    elif args[0] == "-i":
        while (text := input(w("ask")).strip()):
            yes = input(w("askyes")).strip().lower() == "y"
            logs.append(trip(text, confirmed=yes, show_wall=False))
    else:
        logs.append(trip(args[0], confirmed="--yes" in args))
    json.dump(logs, open("walkthrough_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(w("logged", n=len(logs)))
