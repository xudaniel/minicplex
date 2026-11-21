# staffing_agent.py —— 补班 agent 原型：一句话 → 改动单 → 规则把关 → 求解 → 自检 → 说人话
# Staffing agent prototype: one sentence → change request → guard → solve → sanity check → plain words
# 运行 / Run：pip install ortools；python3 staffing_agent.py（中文）或 python3 staffing_agent.py --lang en
# 第 1 步的 parse() 用几条正则顶替 LLM；换成真模型时，只换这一个函数。
# Step 1 (parse) uses a few regexes in place of an LLM; to use a real model, replace only that function.
import re, sys, json
from ortools.linear_solver import pywraplp

BASE = {"demand": 130, "whole": True, "shortage_penalty": 1000,
        "resources": {"派遣": [10, 50, 8], "常勤加排": [8, 32, 8], "加急派遣": [10, 75, 20]},  # 每班次数、每班费用、最多几班 / visits, cost, max shifts
        "rush_rule": True}          # 合同：普通派遣用满，才能叫加急 / contract: fill dispatch before rush
LIMITS = {"demand": (1, 200), "cap": {"派遣": 8, "常勤加排": 8, "加急派遣": 20}, "cost_pct": 30}
APPROVAL_LINE = 50                  # 比基准多花超过 50（千日元）由院长批 / above +50 the director approves
NAMES = {"加急": "加急派遣", "派遣": "派遣", "常勤": "常勤加排",                 # 口语 → 模型里的名字
         "rush": "加急派遣", "dispatch": "派遣", "regular": "常勤加排"}          # spoken word → model name
SHIFT = "加急|派遣|常勤|rush|dispatch|regular"

# ---------- 中英文：模型里的名字不变，只换显示和提示 / one model, two languages ----------
LANG = "zh"
SHOW = {"en": {"派遣": "dispatch", "常勤加排": "regular overtime", "加急派遣": "rush"}}
MSG = {
 "empty":   ("没读出可以改的东西。请说明：是需求、某种班的上限，还是价格？",
             "Found nothing to change. Is it demand, a shift cap, or a price?"),
 "noquote": ("改动没有原文依据：{c}", "This change has no source wording: {c}"),
 "two":     ("这句话里提到不止一种班，改的是哪一种？（读成了：{r} → {v}）",
             "This sentence names more than one shift type. Which one changes? (read as: {r} → {v})"),
 "demand":  ("需求 {v} 次超出合理范围 {lo}–{hi}，请确认数字",
             "Demand of {v} visits is outside {lo}–{hi}; please check the number"),
 "cap":     ("{r} 上限 {v} 班超过合同上限 {cap} 班", "A {r} cap of {v} shifts exceeds the contract cap of {cap}"),
 "price":   ("{r} 价格从 {b} 改到 {v}（{p:+.0f}%），超过 ±{lim}%，要人确认后才算",
             "The {r} price moves from {b} to {v} ({p:+.0f}%), beyond ±{lim}%; a person must confirm before solving"),
 "short":   ("排不出来，还缺 {s:g} 次", "Demand can't be covered; still {s:g} visits short"),
 "rush":    ("普通派遣没用满就用了加急：可能漏了合同规则",
             "Rush used before dispatch is full: the contract rule may be missing"),
 "rulecost": ("派遣（每次 {uk:g}）比{j}（每次 {uj:g}）贵却用满了：这是「先用满派遣才能叫加急」这条合同规则的代价，属正常",
              "Dispatch ({uk:g} per visit) costs more than {j} ({uj:g}) yet is full: that is the price of the contract rule, as expected"),
 "pricey":  ("用了较贵的{k}（每次 {uk:g}），较便宜的{j}（每次 {uj:g}）却没用满：整班凑数造成的可以接受，否则查约束",
             "Used the pricier {k} ({uk:g} per visit) while the cheaper {j} ({uj:g}) is not full: fine if due to whole shifts, otherwise check the constraints"),
 "fix":     ("护士长先定补救办法", "the head nurse decides how to cover the gap first"),
 "director": ("院长批", "the director"),
 "nurse":   ("护士长批", "the head nurse"),
 "item":    ("{n} {v:g} 班", "{n} {v:g} shift{s}"),
 "line":    ("方案：{plan}，费用 {cost:g}（比基准{ml} {d:g}）。审批：{who}。",
             "Plan: {plan}; cost {cost:g} ({d:g} {ml} than baseline). Approval: {who}."),
 "more":    ("多", "more"), "less": ("少", "less"), "sep": ("、", ", "),
 "say":     ("护士长：「{t}」", "Head nurse: “{t}”"),
 "guardsays": ("  把关：", "  Guard: "),
 "stop":    ("  → 停在这里，不求解。", "  → Stops here; nothing is solved."),
 "changes": ("  改动单：", "  Change request: "),
 "base":    ("基准：", "Baseline:"),
}
def t(key, **kw): return MSG[key][LANG == "en"].format(**kw)
def show(r): return SHOW.get(LANG, {}).get(r, r)       # 显示用的名字 / display name

# ---------- 第 1 步：一句话 → 改动单（这里是 LLM 的位置） / Step 1: sentence → change request (the LLM's job) ----------
def parse(text):
    ch, I = [], re.I
    def res(word): return NAMES[word.lower()]
    def between(): return rf"(?:(?!{SHIFT}).)*?"                   # 中间不许出现别的班名 / no other shift name in between
    m = re.search(r"需求.*?(\d+)\s*次|demand.*?(\d+)\s*visits?", text, I)
    if m: ch.append({"type": "demand", "value": int(m.group(1) or m.group(2)), "quote": m.group(0)})
    m = re.search(rf"({SHIFT}){between()}(?:最多|只能|at most|only|max(?:imum)?).*?(\d+)\s*(?:班|(?:extra\s+)?shifts?)", text, I)
    if m: ch.append({"type": "cap", "resource": res(m.group(1)), "value": int(m.group(2)), "quote": m.group(0)})
    m = re.search(rf"({SHIFT}){between()}(?:涨价?\s*(\d+)\s*%|(\d+)\s*%\s*(?:price\s+)?(?:increase|rise|hike)"
                  rf"|(?:up|rais\w*|increas\w*)\s+(?:prices?\s+)?(?:by\s+)?(\d+)\s*%)", text, I)
    if m:
        r = res(m.group(1)); pct = int(m.group(2) or m.group(3) or m.group(4))
        ch.append({"type": "cost", "resource": r, "value": round(BASE["resources"][r][1] * (1 + pct / 100), 1), "quote": m.group(0)})
    m = re.search(rf"({SHIFT}){between()}(?:每班\s*(\d+)|(\d+)\s*(?:per|a|/)\s*shift)", text, I)
    if m: ch.append({"type": "cost", "resource": res(m.group(1)), "value": int(m.group(2) or m.group(3)), "quote": m.group(0)})
    return ch

# ---------- 第 2 步：规则把关（agent 的输出不能直接进模型） / Step 2: guard (agent output never goes straight to the model) ----------
def guard(text, changes):
    if not changes: return "ask", [t("empty")]
    notes, status = [], "ok"
    for c in changes:
        if c["quote"] not in text: return "reject", [t("noquote", c=c)]
        if len(set(NAMES[k.lower()] for k in re.findall(SHIFT, c["quote"], re.I))) > 1:
            return "ask", [t("two", r=show(c.get("resource")), v=c["value"])]
        if c["type"] == "demand" and not LIMITS["demand"][0] <= c["value"] <= LIMITS["demand"][1]:
            return "reject", [t("demand", v=c["value"], lo=LIMITS["demand"][0], hi=LIMITS["demand"][1])]
        if c["type"] == "cap" and not 0 <= c["value"] <= LIMITS["cap"][c["resource"]]:
            return "reject", [t("cap", r=show(c["resource"]), v=c["value"], cap=LIMITS["cap"][c["resource"]])]
        if c["type"] == "cost":
            base = BASE["resources"][c["resource"]][1]; pct = (c["value"] - base) / base * 100
            if abs(pct) > LIMITS["cost_pct"]:
                status = "confirm"; notes.append(t("price", r=show(c["resource"]), b=base, v=c["value"], p=pct, lim=LIMITS["cost_pct"]))
    return status, notes

# ---------- 第 3 步：求解 / Step 3: solve ----------
def apply(changes):
    m = json.loads(json.dumps(BASE))   # 复印一份，原件不动 / work on a copy; the baseline never changes
    for c in changes:
        if c["type"] == "demand": m["demand"] = c["value"]
        if c["type"] == "cap": m["resources"][c["resource"]][2] = c["value"]
        if c["type"] == "cost": m["resources"][c["resource"]][1] = c["value"]
    return m
def solve(m):
    s = pywraplp.Solver.CreateSolver("SCIP"); R = m["resources"]
    x = {k: (s.IntVar if m["whole"] else s.NumVar)(0, cap, k) for k, (_, _, cap) in R.items()}
    short = s.NumVar(0, s.infinity(), "short")
    s.Add(sum(R[k][0] * x[k] for k in R) + short >= m["demand"])
    if m["rush_rule"]:
        y = s.BoolVar("y"); s.Add(x["加急派遣"] <= R["加急派遣"][2] * y); s.Add(x["派遣"] >= R["派遣"][2] * y)
    s.Minimize(sum(R[k][1] * x[k] for k in R) + m["shortage_penalty"] * short); s.Solve()
    plan = {k: round(x[k].solution_value(), 2) + 0.0 for k in R}
    return {"plan": plan, "cost": round(sum(R[k][1] * plan[k] for k in R), 1), "short": round(short.solution_value(), 1) + 0.0}

# ---------- 第 4 步：自检（答案「怪不怪」）和审批门槛 / Step 4: sanity check and approval ----------
def sanity(m, r):
    R, p, flags = m["resources"], r["plan"], []
    if r["short"] > 0: flags.append(t("short", s=r["short"]))
    if p["加急派遣"] > 0 and p["派遣"] < R["派遣"][2]: flags.append(t("rush"))
    unit = {k: R[k][1] / R[k][0] for k in R}
    for k in R:
        for j in R:
            if p[k] > 0 and p[j] < R[j][2] and unit[j] < unit[k] - 1e-9 and not (m["whole"] and R[j][2] - p[j] < 1):
                if m["rush_rule"] and k == "派遣" and p["加急派遣"] > 0:
                    flags.append(t("rulecost", uk=unit[k], j=show(j), uj=unit[j])); continue
                flags.append(t("pricey", k=show(k), uk=unit[k], j=show(j), uj=unit[j]))
    return flags
def approver(r, base):
    if r["short"] > 0: return t("fix")
    return t("director") if r["cost"] - base["cost"] > APPROVAL_LINE else t("nurse")

# ---------- 第 5 步：说人话（数字只来自求解器） / Step 5: plain words (numbers come only from the solver) ----------
def explain(r, base, flags, who):
    plan = t("sep").join(t("item", n=show(k), v=v, s="" if v == 1 else "s") for k, v in r["plan"].items() if v > 0)
    d = r["cost"] - base["cost"]
    line = t("line", plan=plan, cost=r["cost"], ml=t("more") if d >= 0 else t("less"), d=abs(d), who=who)
    return line + ("".join(f"\n    ⚠ {f}" for f in flags))

def run(text, confirmed=False, model_override=None, changes=None):
    print("\n" + t("say", t=text))
    changes = changes if changes is not None else parse(text); status, notes = guard(text, changes)
    log = {"text": text, "changes": changes, "guard": status, "notes": notes}
    for n in notes: print(t("guardsays") + n)
    if status in ("ask", "reject") or (status == "confirm" and not confirmed):
        print(t("stop")); return log
    m = apply(changes)
    if model_override: m.update(model_override)
    base = solve(BASE); r = solve(m); flags = sanity(m, r)
    print(t("changes") + json.dumps([{k: show(v) if k == "resource" else v for k, v in c.items() if k != "quote"} for c in changes], ensure_ascii=False))
    print("  " + explain(r, base, flags, approver(r, base)))
    log.update(result=r, flags=flags, approver=approver(r, base)); return log

# 九句测试话，中英文各一套；第 6 句模拟「模型读错」：把加急的价格记到了普通派遣头上
# Nine test sentences in each language; no. 6 simulates a misread: the rush price is put on dispatch
CASES = {
 "zh": ["下周三有人请假，常勤最多只能加 4 班", "病房说下周需求可能到 140 次", "派遣公司通知涨价 10%",
        "让小王别上太多班，大概两三班吧", "需求改成 1300 次", "派遣公司说加急每班 40，多用点加急吧", "派遣公司说加急每班 40"],
 "en": ["Someone is off next Wednesday, so regular staff can do at most 4 extra shifts",
        "The ward says demand next week may reach 140 visits", "The dispatch agency announced a 10% price increase",
        "Don't let Sam work too many shifts, maybe two or three", "Change demand to 1300 visits",
        "The dispatch agency says rush shifts are 40 per shift", "The dispatch agency says rush shifts are 40"],
}

if __name__ == "__main__":
    if "--lang" in sys.argv: LANG = sys.argv[sys.argv.index("--lang") + 1]
    c = CASES[LANG]; wrong = c[6]
    b = solve(BASE); print(t("base"), {show(k): v for k, v in b["plan"].items()}, b["cost"])
    logs = [run(c[0]), run(c[1]), run(c[2]), run(c[3]), run(c[4]),
            run(c[5], changes=[{"type": "cost", "resource": "派遣", "value": 40, "quote": wrong}]),
            run(c[5]), run(c[5], confirmed=True), run(c[5], confirmed=True, model_override={"rush_rule": False})]
    json.dump(logs, open("audit_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
