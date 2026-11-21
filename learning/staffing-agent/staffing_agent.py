# staffing_agent.py —— 补班 agent 原型：一句话 → 改动单 → 规则把关 → 求解 → 自检 → 说人话
# 运行：pip install ortools；python3 staffing_agent.py
# 第 1 步的 parse() 用几条正则顶替 LLM，只为让整条链能跑；换成真模型时，只换这一个函数。
import re, json
from ortools.linear_solver import pywraplp

BASE = {"demand": 130, "whole": True, "shortage_penalty": 1000,
        "resources": {"派遣": [10, 50, 8], "常勤加排": [8, 32, 8], "加急派遣": [10, 75, 20]},  # 每班次数、每班费用、最多几班
        "rush_rule": True}          # 合同：普通派遣用满，才能叫加急
LIMITS = {"demand": (1, 200), "cap": {"派遣": 8, "常勤加排": 8, "加急派遣": 20}, "cost_pct": 30}
APPROVAL_LINE = 50                  # 比基准多花超过 50（千日元）由院长批
NAMES = {"加急": "加急派遣", "派遣": "派遣", "常勤": "常勤加排"}

# ---------- 第 1 步：一句话 → 改动单（这里是 LLM 的位置） ----------
def parse(text):
    ch = []
    m = re.search(r"需求.*?(\d+)\s*次", text)
    if m: ch.append({"type": "demand", "value": int(m.group(1)), "quote": m.group(0)})
    m = re.search(r"(加急|派遣|常勤)(?:(?!加急|派遣|常勤).)*?(?:最多|只能).*?(\d+)\s*班", text)
    if m: ch.append({"type": "cap", "resource": NAMES[m.group(1)], "value": int(m.group(2)), "quote": m.group(0)})
    m = re.search(r"(加急|派遣|常勤)(?:(?!加急|派遣|常勤).)*?涨价?\s*(\d+)\s*%", text)
    if m:
        r = NAMES[m.group(1)]; ch.append({"type": "cost", "resource": r, "value": round(BASE["resources"][r][1] * (1 + int(m.group(2)) / 100), 1), "quote": m.group(0)})
    m = re.search(r"(加急|派遣|常勤)(?:(?!加急|派遣|常勤).)*?每班\s*(\d+)", text)
    if m: ch.append({"type": "cost", "resource": NAMES[m.group(1)], "value": int(m.group(2)), "quote": m.group(0)})
    return ch

# ---------- 第 2 步：规则把关（agent 的输出不能直接进模型） ----------
def guard(text, changes):
    if not changes: return "ask", ["没读出可以改的东西。请说明：是需求、某种班的上限，还是价格？"]
    notes, status = [], "ok"
    for c in changes:
        if c["quote"] not in text: return "reject", [f"改动没有原文依据：{c}"]
        if len(set(NAMES[k] for k in re.findall("加急|派遣|常勤", c["quote"]))) > 1:
            return "ask", [f"这句话里提到不止一种班，改的是哪一种？（读成了：{c.get('resource')} → {c['value']}）"]
        if c["type"] == "demand" and not LIMITS["demand"][0] <= c["value"] <= LIMITS["demand"][1]:
            return "reject", [f"需求 {c['value']} 次超出合理范围 {LIMITS['demand']}，请确认数字"]
        if c["type"] == "cap" and not 0 <= c["value"] <= LIMITS["cap"][c["resource"]]:
            return "reject", [f"{c['resource']} 上限 {c['value']} 班超过合同上限 {LIMITS['cap'][c['resource']]} 班"]
        if c["type"] == "cost":
            base = BASE["resources"][c["resource"]][1]; pct = (c["value"] - base) / base * 100
            if abs(pct) > LIMITS["cost_pct"]:
                status = "confirm"; notes.append(f"{c['resource']} 价格从 {base} 改到 {c['value']}（{pct:+.0f}%），超过 ±{LIMITS['cost_pct']}%，要人确认后才算")
    return status, notes

# ---------- 第 3 步：求解 ----------
def apply(changes):
    m = json.loads(json.dumps(BASE))
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
    plan = {k: round(x[k].solution_value(), 2) for k in R}
    return {"plan": plan, "cost": round(sum(R[k][1] * plan[k] for k in R), 1), "short": round(short.solution_value(), 1)}

# ---------- 第 4 步：自检（答案「怪不怪」）和审批门槛 ----------
def sanity(m, r):
    R, p, flags = m["resources"], r["plan"], []
    if r["short"] > 0: flags.append(f"排不出来，还缺 {r['short']:g} 次")
    if p["加急派遣"] > 0 and p["派遣"] < R["派遣"][2]: flags.append("普通派遣没用满就用了加急：可能漏了合同规则")
    unit = {k: R[k][1] / R[k][0] for k in R}
    for k in R:
        for j in R:
            if p[k] > 0 and p[j] < R[j][2] and unit[j] < unit[k] - 1e-9 and not (m["whole"] and R[j][2] - p[j] < 1):
                if m["rush_rule"] and k == "派遣" and p["加急派遣"] > 0:
                    flags.append(f"派遣（每次 {unit[k]:g}）比{j}（每次 {unit[j]:g}）贵却用满了：这是「先用满派遣才能叫加急」这条合同规则的代价，属正常"); continue
                flags.append(f"用了较贵的{k}（每次 {unit[k]:g}），较便宜的{j}（每次 {unit[j]:g}）却没用满：整班凑数造成的可以接受，否则查约束")
    return flags
def approver(r, base):
    if r["short"] > 0: return "护士长先定补救办法"
    return "院长批" if r["cost"] - base["cost"] > APPROVAL_LINE else "护士长批"

# ---------- 第 5 步：说人话（数字只来自求解器） ----------
def explain(r, base, flags, who):
    plan = "、".join(f"{k} {v:g} 班" for k, v in r["plan"].items() if v > 0)
    d = r["cost"] - base["cost"]
    line = f"方案：{plan}，费用 {r['cost']:g}（比基准{'多' if d >= 0 else '少'} {abs(d):g}）。审批：{who}。"
    return line + ("".join(f"\n    ⚠ {f}" for f in flags))

def run(text, confirmed=False, model_override=None, changes=None):
    print(f"\n护士长：「{text}」")
    changes = changes if changes is not None else parse(text); status, notes = guard(text, changes)
    log = {"text": text, "changes": changes, "guard": status, "notes": notes}
    for n in notes: print("  把关：" + n)
    if status in ("ask", "reject") or (status == "confirm" and not confirmed):
        print("  → 停在这里，不求解。"); return log
    m = apply(changes)
    if model_override: m.update(model_override)
    base = solve(BASE); r = solve(m); flags = sanity(m, r)
    print("  改动单：" + json.dumps([{k: v for k, v in c.items() if k != "quote"} for c in changes], ensure_ascii=False))
    print("  " + explain(r, base, flags, approver(r, base)))
    log.update(result=r, flags=flags, approver=approver(r, base)); return log

if __name__ == "__main__":
    b = solve(BASE); print("基准：", b)
    logs = [run("下周三有人请假，常勤最多只能加 4 班"),
            run("病房说下周需求可能到 140 次"),
            run("派遣公司通知涨价 10%"),
            run("让小王别上太多班，大概两三班吧"),
            run("需求改成 1300 次"),
            run("派遣公司说加急每班 40，多用点加急吧",   # 模拟模型读错：把加急的价格记到了普通派遣头上
                changes=[{"type": "cost", "resource": "派遣", "value": 40, "quote": "派遣公司说加急每班 40"}]),
            run("派遣公司说加急每班 40，多用点加急吧"),
            run("派遣公司说加急每班 40，多用点加急吧", confirmed=True),
            run("派遣公司说加急每班 40，多用点加急吧", confirmed=True, model_override={"rush_rule": False})]
    json.dump(logs, open("audit_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
