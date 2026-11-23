# itinerary_agent.py —— 旅行行程 agent：一句话 → 改动单 → 门卫 → 排程求解 → 老师傅 → 说人话
# Trip itinerary agent: one sentence → change request → guard → schedule → sanity check → plain words
# 运行 / Run：pip install ortools
#   python3 itinerary_agent.py               主角那句话，逐站打印 / the main sentence, station by station
#   python3 itinerary_agent.py --all         主角 + 翻车现场 + 考考你 / plus failures and quiz
#   python3 itinerary_agent.py -i            自己输入，空行退出 / type your own; empty line quits
#   python3 itinerary_agent.py "第二天下午五点前要回酒店"
#   任何一种加 --lang en 就是英文 / add --lang en to any of them for English
# 城市、景点、时间、分数都是虚构的 / the city, sights, hours and scores are all invented.
import re, sys, json
from ortools.sat.python import cp_model

# ---------- 第 0 站：墙上的规矩 / Station 0: the rules on the wall ----------
DAYS = {1: [15 * 60, 21 * 60], 2: [9 * 60, 20 * 60], 3: [9 * 60, 12 * 60]}  # 到达日下午、整天、回程日 / arrival afternoon, full day, flight home
TRAVEL = 30            # 两个景点之间路上 30 分钟 / 30 minutes between any two sights
MAX_ZONES = 2          # 每天最多跑两个区 / at most two districts a day
LUNCH = (11 * 60 + 30, 13 * 60, 60)   # 午饭 11:30–13:00 之间开吃，吃 60 分钟；拉面横丁也算 / lunch starts 11:30–13:00, 60 min; Ramen Alley counts
#            中文名          英文名               区    想去指数 玩多久  开门      关门
SIGHTS = {"千灯寺":   ["Lantern Temple",   "东", 9, 120,  8 * 60, 17 * 60],
          "竹林小径": ["Bamboo Path",      "东", 7,  60,  6 * 60, 18 * 60],
          "天守阁":   ["Castle Keep",      "中", 10, 120, 9 * 60, 17 * 60],
          "海边市场": ["Seaside Market",   "西", 8, 120,  7 * 60, 13 * 60],
          "美术馆":   ["Art Museum",       "中", 6, 120, 10 * 60, 18 * 60],
          "温泉街":   ["Onsen Street",     "西", 8, 180, 13 * 60, 22 * 60],
          "夜市":     ["Night Market",     "中", 7, 120, 18 * 60, 23 * 60],
          "观景台":   ["Skyview Deck",     "东", 6,  60, 10 * 60, 22 * 60],
          "拉面横丁": ["Ramen Alley",      "中", 5,  60, 11 * 60, 22 * 60],
          "动物园":   ["Zoo",              "西", 5, 180,  9 * 60, 17 * 60]}
TICKETS = {"天守阁": (2, 14 * 60)}   # 已买票：第 2 天 14:00 入场 / booked: day 2, 14:00
BASE = {"days": DAYS, "must": [], "skip": [], "zone_rule": True, "lunch_rule": True}
LIMITS = {"hour": (5, 24)}
SCORE_DROP = 5         # 想去指数少 5 分以上，要同行的人一起商量 / a drop of 5+ needs the group to agree

LANG = "zh"
ZONE_EN = {"东": "East", "中": "Center", "西": "West"}
MSG = {
 "empty":   ("没读出要改什么。是哪天几点开始／结束，还是哪个景点要去／不去？",
             "Found nothing to change. Is it a start or end time for a day, or a sight to add or drop?"),
 "noquote": ("改动没有原文依据：{c}", "This change has no source wording: {c}"),
 "unknown": ("名单里没有「{n}」，是指哪一个？", "“{n}” is not on the list. Which sight do you mean?"),
 "day":     ("第 {d} 天不在行程里（只有 {n} 天）", "Day {d} is not in the trip (only {n} days)"),
 "hour":    ("{h} 点不像是合理的时间，请确认", "{h}:00 does not look like a sensible time; please check"),
 "both":    ("「{n}」又要去又不去，到底去不去？", "“{n}” is both added and dropped. Which is it?"),
 "window":  ("第 {d} 天开始 {s} 已经晚于结束 {e}，这天没法安排", "Day {d} would start at {s}, after it ends at {e}"),
 "ticket":  ("「{n}」的票已经买了（第 {d} 天 {t}），不去要退票，要人确认", "Tickets for {n} are booked (day {d}, {t}); dropping it means a refund, so a person must confirm"),
 "empty_day": ("第 {d} 天一个景点都没排", "Day {d} has nothing planned"),
 "lunch":   ("第 {d} 天中午没留吃饭的时间（模型不知道人要吃午饭）", "Day {d} leaves no time for lunch (the model doesn't know people eat)"),
 "zones":   ("第 {d} 天跑了 {n} 个区：模型把每段路都当 30 分钟，跨区其实更远", "Day {d} covers {n} districts: the model counts every leg as 30 minutes, but crossing town takes longer"),
 "missed":  ("最想去的「{n}」（{s} 分）没排上", "Top pick {n} (score {s}) did not make it"),
 "pay":     ("出钱的人批（要退改门票）", "whoever paid signs (tickets must be changed)"),
 "group":   ("同行的人一起商量", "the whole group decides"),
 "self":    ("自己定就行", "your call"),
 "dayname": ("第 {d} 天", "Day {d}"), "free": ("空着", "free"), "sep": ("；", "; "),
 "line":    ("想去指数 {s}（比原计划{ml} {d}）。审批：{who}。", "Want-to-go score {s} ({d} {ml} than the original plan). Approval: {who}."),
 "more":    ("多", "more"), "less": ("少", "less"), "comma": ("，", ", "),
 "same":    ("想去指数 {s}（和原计划一样）。审批：{who}。", "Want-to-go score {s} (same as the original plan). Approval: {who}."),
}
def t(key, **kw): return MSG[key][LANG == "en"].format(**kw)
def name(s): return SIGHTS[s][0] if LANG == "en" and s in SIGHTS else s
def hm(m): return f"{m // 60:02d}:{m % 60:02d}"

# ---------- 第 1 站：助理 parse，一句话 → 纸条 / Station 1: the assistant reads the sentence ----------
CN = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
EN = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
NZ, NE = r"\d{1,2}|[一二两三四五六七八九十]{1,3}", r"\d{1,2}|" + "|".join(EN)
def num(s):
    s = s.lower()
    if s.isdigit(): return int(s)
    if s in EN: return EN[s]
    if "十" not in s: return CN[s]
    tens, _, ones = s.partition("十")                 # 十=10，十二=12，二十=20 / Chinese numerals
    return (CN[tens] if tens else 1) * 10 + (CN[ones] if ones else 0)
def hour(h, tag):
    h = num(h)
    return h + 12 if tag and tag.lower() in ("下午", "晚上", "pm") and h < 12 else h
def sight(raw):
    raw = re.sub(rf"^第\s*(?:{NZ})\s*天", "", raw).strip()
    for s, info in SIGHTS.items():
        if s in raw or info[0].lower() in raw.lower(): return s
    return raw                                  # 不认识就原样交出，让门卫去问 / unknown: pass it on for the guard to ask

def parse(text):
    ch, I = [], re.I
    for kind, zh, en in [
        ("start", rf"第\s*({NZ})\s*天.*?(上午|下午|晚上)?\s*({NZ})\s*点(?:之|以)?前\s*(?:别|不要|不)",
                  rf"day\s*({NE})\b.*?(?:nothing|no plans?)\s*(?:planned\s*)?before\s*({NE})\s*(am|pm)?"),
        ("end",   rf"第\s*({NZ})\s*天.*?(上午|下午|晚上)?\s*({NZ})\s*点(?:之|以)?前\s*(?:要)?(?:回|结束|收工)",
                  rf"day\s*({NE})\b.*?back(?:\s+at\s+the\s+hotel)?\s*(?:by|before)\s*({NE})\s*(am|pm)?")]:
        m = re.search(zh, text)
        if m: ch.append({"type": kind, "day": num(m.group(1)), "value": hour(m.group(3), m.group(2)), "quote": m.group(0)})
        m = re.search(en, text, I)
        if m: ch.append({"type": kind, "day": num(m.group(1)), "value": hour(m.group(2), m.group(3)), "quote": m.group(0)})
    for kind, pats in [("must", [r"([^，,。；;\s]+?)(?:一定|必须|非得?)要去", r"(?:一定|必须)要去\s*([^，,。；;\s]+)",
                                 r"(?:must|have to|definitely)\s+(?:see|visit|go to)\s+(?:the\s+)?([A-Za-z][A-Za-z ]*?)\s*(?=[,.;!]|$)"]),
                       ("skip", [r"([^，,。；;\s]+?)(?:不去了|别去了|不想去了)",
                                 r"(?:skip|drop)\s+(?:the\s+)?([A-Za-z][A-Za-z ]*?)\s*(?=[,.;!]|$)"])]:
        for p in pats:
            for m in re.finditer(p, text, I):
                ch.append({"type": kind, "sight": sight(m.group(1)), "quote": m.group(0)})
    return ch

# ---------- 第 2 站：门卫 guard / Station 2: the gatekeeper ----------
def guard(text, changes):
    if not changes: return "ask", [t("empty")]
    notes, status = [], "ok"
    for c in changes:
        if c["quote"] not in text: return "reject", [t("noquote", c=c)]                       # 1 真是你说的吗
        if "sight" in c and c["sight"] not in SIGHTS: return "ask", [t("unknown", n=c["sight"])]  # 2 说的是哪一个
        if "day" in c and c["day"] not in DAYS: return "reject", [t("day", d=c["day"], n=len(DAYS))]  # 3 数字合理吗
        if "value" in c and not LIMITS["hour"][0] <= c["value"] <= LIMITS["hour"][1]:
            return "reject", [t("hour", h=c["value"])]
    must = {c["sight"] for c in changes if c["type"] == "must"}
    for c in changes:
        if c["type"] == "skip" and c["sight"] in must: return "ask", [t("both", n=name(c["sight"]))]
    m = apply(changes)
    for d, (s, e) in m["days"].items():
        if s >= e: return "reject", [t("window", d=d, s=hm(s), e=hm(e))]
    for c in changes:                                                                          # 4 要不要人签字
        if c["type"] == "skip" and c["sight"] in TICKETS:
            d, st = TICKETS[c["sight"]]; status = "confirm"; notes.append(t("ticket", n=name(c["sight"]), d=d, t=hm(st)))
    return status, notes

# ---------- 第 3 站：会计 apply + solve / Station 3: the accountant ----------
def apply(changes):
    m = json.loads(json.dumps(BASE)); m["days"] = {int(k): v for k, v in m["days"].items()}   # 复印一份 / work on a copy
    for c in changes:
        if c["type"] == "start": m["days"][c["day"]][0] = max(m["days"][c["day"]][0], c["value"] * 60)
        if c["type"] == "end":   m["days"][c["day"]][1] = min(m["days"][c["day"]][1], c["value"] * 60)
        if c["type"] in ("must", "skip"): m[c["type"]].append(c["sight"])
    return m

def solve(m):
    md, S = cp_model.CpModel(), SIGHTS
    x, st, ivs = {}, {}, {d: [] for d in m["days"]}
    for s, (_, zone, score, dur, op, cl) in S.items():
        for d, (ds, de) in m["days"].items():
            x[s, d] = md.NewBoolVar(f"x_{s}_{d}")                     # 第 d 天去不去 s / visit s on day d?
            st[s, d] = md.NewIntVar(0, 24 * 60, f"st_{s}_{d}")        # 几点到 / arrival minute
            md.Add(st[s, d] >= max(op, ds)).OnlyEnforceIf(x[s, d])     # 开门了、这天也开始了 / open, and the day has begun
            md.Add(st[s, d] + dur <= min(cl, de)).OnlyEnforceIf(x[s, d])  # 关门前、收工前玩完 / done before closing and day end
            md.Add(st[s, d] == 0).OnlyEnforceIf(x[s, d].Not())
            ivs[d].append(md.NewOptionalIntervalVar(st[s, d], dur + TRAVEL, st[s, d] + dur + TRAVEL, x[s, d], f"iv_{s}_{d}"))
        visits = sum(x[s, d] for d in m["days"])
        md.Add(visits == (0 if s in m["skip"] else 1) if s in m["skip"] or s in m["must"] else visits <= 1)
        if s in TICKETS and s not in m["skip"]:
            d, t0 = TICKETS[s]; md.Add(x[s, d] == 1); md.Add(st[s, d] == t0)     # 票上的时间 / the ticketed slot
    if m["lunch_rule"]:
        lo, hi, dur = LUNCH
        for d, (ds, de) in m["days"].items():
            if ds > lo or de < hi + dur: continue                     # 这天不跨午饭时间 / day doesn't span lunch
            eat = md.NewBoolVar(f"lunch_{d}"); ls = md.NewIntVar(lo, hi, f"ls_{d}")
            ivs[d].append(md.NewOptionalIntervalVar(ls, dur + TRAVEL, ls + dur + TRAVEL, eat, f"lunch_iv_{d}"))
            ramen = md.NewBoolVar(f"ramen_{d}")                       # 中午去拉面横丁就当吃过了 / ramen at noon counts as lunch
            md.AddImplication(ramen, x["拉面横丁", d])
            md.Add(st["拉面横丁", d] >= lo - 30).OnlyEnforceIf(ramen); md.Add(st["拉面横丁", d] <= hi).OnlyEnforceIf(ramen)
            md.AddBoolOr([eat, ramen])
    for d in m["days"]: md.AddNoOverlap(ivs[d])                       # 同一天不能同时在两处，含路上 30 分钟 / one place at a time, incl. travel
    if m["zone_rule"]:
        for d in m["days"]:
            used = {z: md.NewBoolVar(f"z_{d}_{z}") for z in ZONE_EN}
            for s, info in S.items(): md.AddImplication(x[s, d], used[info[1]])
            md.Add(sum(used.values()) <= MAX_ZONES)                    # 每天最多两个区 / at most two districts
    score = sum(S[s][2] * x[s, d] for s in S for d in m["days"])
    md.Maximize(100000 * score - sum(st.values()))                    # 先比想去指数，同分时越早越好 / score first, then earlier
    sv = cp_model.CpSolver(); sv.parameters.num_workers = 1; sv.parameters.random_seed = 0
    status = sv.Solve(md)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), sv.StatusName(status)
    plan = {d: sorted((sv.Value(st[s, d]), s) for s in S if sv.Value(x[s, d])) for d in m["days"]}
    return {"plan": plan, "score": int(sum(S[s][2] for d in plan for _, s in plan[d]))}

# ---------- 第 4 站：老师傅 sanity + approver / Station 4: the experienced colleague ----------
def sanity(m, r):
    flags, chosen = [], {s for d in r["plan"] for _, s in r["plan"][d]}
    for d, items in r["plan"].items():
        if not items: flags.append(t("empty_day", d=d)); continue
        ds, de = m["days"][d]
        if ds <= LUNCH[0] and de >= LUNCH[1] + LUNCH[2] and not lunch(items):
            flags.append(t("lunch", d=d))
        zones = {SIGHTS[s][1] for _, s in items}
        if len(zones) > MAX_ZONES: flags.append(t("zones", d=d, n=len(zones)))
    for s, info in SIGHTS.items():
        if info[2] >= 9 and s not in chosen and s not in m["skip"]: flags.append(t("missed", n=name(s), s=info[2]))
    return flags

def lunch(items):
    """中午吃过拉面，或者 11:30–13:00 能开吃 60 分钟 / ramen at noon, or a 60-minute lunch slot starting 11:30–13:00"""
    lo, hi, dur = LUNCH
    if any(s == "拉面横丁" and lo - 30 <= a <= hi for a, s in items): return True
    busy = sorted((a, a + SIGHTS[s][3] + TRAVEL) for a, s in items)
    for start in range(lo, hi + 1, 5):                               # 找一个 60 分钟 + 路上 30 分钟的空档 / look for a free slot
        if all(start + dur + TRAVEL <= a or start >= b for a, b in busy): return True
    return False

def approver(r, base):
    def where(res, s): return next(((d, a) for d in res["plan"] for a, x in res["plan"][d] if x == s), None)
    if any(where(r, s) != where(base, s) for s in TICKETS): return t("pay")
    return t("group") if base["score"] - r["score"] >= SCORE_DROP else t("self")

# ---------- 第 5 站：秘书 explain / Station 5: the secretary ----------
def timetable(r):
    return t("sep").join(t("dayname", d=d) + ": " + (" → ".join(f"{hm(a)} {name(s)}" for a, s in items) or t("free"))
                         for d, items in r["plan"].items())
def explain(r, base, flags, who):
    d = r["score"] - base["score"]
    tail = t("same", s=r["score"], who=who) if d == 0 else t("line", s=r["score"], ml=t("more") if d > 0 else t("less"), d=abs(d), who=who)
    line = timetable(r) + "\n  " + tail
    return line + "".join(f"\n    ⚠ {f}" for f in flags)

# ---------- 边跑边讲 / narrate every station ----------
W = {"s0": ("第 0 站｜墙上的规矩", "Station 0 | The rules on the wall"),
     "s1": ("第 1 站｜助理：一句话 → 纸条", "Station 1 | Assistant: sentence → note"),
     "s2": ("第 2 站｜门卫：能不能放行", "Station 2 | Gatekeeper: may it pass?"),
     "s3": ("第 3 站｜会计：复印、出题、交给 CP-SAT", "Station 3 | Accountant: copy, model, hand to CP-SAT"),
     "s4": ("第 4 站｜老师傅：怪不怪、谁签字", "Station 4 | Experienced colleague: anything odd? who signs?"),
     "s5": ("第 5 站｜秘书：说成人话", "Station 5 | Secretary: plain words"),
     "row": ("  {n}｜{z}区｜想去 {s}｜玩 {h:g} 小时｜{o}–{c}", "  {n} | {z} | score {s} | {h:g} h | {o}–{c}"),
     "days": ("  每天：", "  Days: "), "rules": ("  规矩：路上 {t} 分钟；每天最多 {z} 个区；{n} 已买票（第 {d} 天 {a}）",
              "  Rules: {t} min between sights; at most {z} districts a day; {n} booked (day {d}, {a})"),
     "in": ("  进：", "  In: "), "out": ("  出：", "  Out: "), "none": ("  一张模板都没套上 → 空纸条", "  No template fits → empty note"),
     "verdict": ("  门卫：{s}（ok 放行／ask 反问／reject 拒绝／confirm 要确认）", "  Gatekeeper: {s} (ok pass / ask / reject / confirm)"),
     "says": ("  门卫说：", "  Gatekeeper: "),
     "stop": ("  🔴 急停：门卫没放行，会计不开工。", "  🔴 Emergency stop: the gatekeeper said no; the accountant never starts."),
     "copy": ("  复印件每天：{d}；BASE 原件第 3 天仍从 {b} 开始（没被改）", "  Copy, per day: {d}; the BASE original still starts day 3 at {b} (untouched)"),
     "override": ("  ⚠ 测试按钮：题目被改成 {o}", "  ⚠ Test switch: the model was changed to {o}"),
     "check": ("  逐项核对：", "  Check each stop:"),
     "base": ("  原计划：", "  Original: "), "new": ("  新方案：", "  New plan: "),
     "item": ("    {d}｜{a}–{b} {n}（开 {o}–{c}）{ok}", "    {d} | {a}–{b} {n} (open {o}–{c}) {ok}"),
     "gap": ("    {d}｜{n1} → {n2} 中间隔 {g} 分钟（要 ≥ {t}）{ok}", "    {d} | {n1} → {n2}: gap {g} min (need ≥ {t}) {ok}"),
     "score": ("  想去指数：{e} = {s}（原计划 {b}）", "  Want-to-go score: {e} = {s} (original {b})"),
     "flags": ("  黄灯：", "  Yellow flags: "), "noflag": ("没有", "none"), "who": ("  签字：", "  Signs: "),
     "confirmed": ("（已确认）", " (confirmed)"), "say": ("「{t}」", "“{t}”"),
     "ask": ("\n说一句（空行退出）：", "\nSay something (empty line quits): "), "askyes": ("要确认的改动算不算？(y/N) ", "Treat confirmations as confirmed? (y/N) ")}
def w(k, **kw): return W[k][LANG == "en"].format(**kw)
def hr(title): print(f"\n{'─' * 5} {title} {'─' * 5}")

def run(text, confirmed=False, override=None, changes=None, wall=True, quiet=False):
    say = (lambda *a: None) if quiet else print
    say(f"\n{'═' * 36}\n" + w("say", t=text) + (w("confirmed") if confirmed else ""))
    if wall and not quiet:
        hr(w("s0"))
        for s, (en, z, sc, dur, o, c) in SIGHTS.items():
            print(w("row", n=name(s), z=ZONE_EN[z] if LANG == "en" else z, s=sc, h=dur / 60, o=hm(o), c=hm(c)))
        print(w("days") + t("comma").join(f"{t('dayname', d=d)} {hm(a)}–{hm(b)}" for d, (a, b) in DAYS.items()))
        n, (d, a) = next(iter(TICKETS.items()))
        print(w("rules", t=TRAVEL, z=MAX_ZONES, n=name(n), d=d, a=hm(a)))
    if not quiet: hr(w("s1")); print(w("in") + text)
    if changes is None: changes = parse(text)
    if not quiet:
        if not changes: print(w("none"))
        print(w("out") + json.dumps([{k: name(v) if k == "sight" else v for k, v in c.items()} for c in changes], ensure_ascii=False))
        hr(w("s2"))
    status, notes = guard(text, changes)
    for n in notes: say(w("says") + n)
    say(w("verdict", s=status))
    log = {"text": text, "changes": changes, "guard": status, "notes": notes}
    if status in ("ask", "reject") or (status == "confirm" and not confirmed):
        say(w("stop")); return log
    m = apply(changes)
    if override: m.update(override)
    base, r = solve(BASE), solve(m)
    if not quiet:
        hr(w("s3"))
        if override: print(w("override", o=override))
        print(w("copy", d=t("comma").join(f"{hm(a)}–{hm(b)}" for a, b in m["days"].values()), b=hm(BASE["days"][3][0])))
        print(w("base") + timetable(base)); print(w("new") + timetable(r))
        print(w("check"))
        for d, items in r["plan"].items():
            for i, (a, s) in enumerate(items):
                o, c, dur = SIGHTS[s][4], SIGHTS[s][5], SIGHTS[s][3]
                ok = "✓" if max(o, m["days"][d][0]) <= a and a + dur <= min(c, m["days"][d][1]) else "✗"
                print(w("item", d=t("dayname", d=d), a=hm(a), b=hm(a + dur), n=name(s), o=hm(o), c=hm(c), ok=ok))
                if i:
                    pa, ps = items[i - 1]; g = a - (pa + SIGHTS[ps][3])
                    print(w("gap", d=t("dayname", d=d), n1=name(ps), n2=name(s), g=g, t=TRAVEL, ok="✓" if g >= TRAVEL else "✗"))
        e = " + ".join(str(SIGHTS[s][2]) for d in r["plan"] for _, s in r["plan"][d])
        print(w("score", e=e, s=r["score"], b=base["score"]))
    flags, who = sanity(m, r), approver(r, base)
    if not quiet:
        hr(w("s4")); print(w("flags") + ("" if flags else w("noflag")))
        for f in flags: print("    ⚠ " + f)
        print(w("who") + who); hr(w("s5"))
    say("  " + explain(r, base, flags, who))
    log.update(result=r, flags=flags, approver=who); return log

SENT = {
 "zh": {"main": "第三天想睡懒觉，十点前别安排", "back": "第二天下午五点前要回酒店", "ticket": "天守阁不去了",
        "unknown": "环球影城一定要去", "day9": "第五天十点前别安排", "both": "美术馆一定要去，美术馆不去了",
        "zoo": "动物园一定要去"},
 "en": {"main": "I want to sleep in on day three, nothing before ten", "back": "On day two we need to be back at the hotel by 5 pm",
        "ticket": "Let's skip the Castle Keep", "unknown": "We have to go to Universal Studios",
        "day9": "Day five, nothing before ten", "both": "We must see the Art Museum, and let's skip the Art Museum",
        "zoo": "We must see the Zoo"},
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--lang" in args: i = args.index("--lang"); LANG = args[i + 1]; del args[i:i + 2]
    S, logs = SENT[LANG], []
    if not args: logs.append(run(S["main"]))
    elif args[0] == "--all":
        logs.append(run(S["main"]))
        logs.append(run(S["back"], wall=False))
        for k in ("unknown", "day9", "both", "ticket"): logs.append(run(S[k], wall=False))
        logs.append(run(S["ticket"], confirmed=True, wall=False))
        logs.append(run(S["main"], override={"lunch_rule": False}, wall=False))  # 😈 拿掉午饭规则 / drop the lunch rule
        logs.append(run(S["zoo"], wall=False))
        logs.append(run(S["zoo"], override={"zone_rule": False}, wall=False))     # 😈 拿掉「每天最多两个区」/ drop the district rule
    elif args[0] == "-i":
        while (txt := input(w("ask")).strip()):
            logs.append(run(txt, confirmed=input(w("askyes")).strip().lower() == "y", wall=False))
    else: logs.append(run(args[0], confirmed="--yes" in args))
    json.dump(logs, open("itinerary_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
