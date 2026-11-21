# walkthrough.py —— 跟着一张纸条走一趟：把五站的输入、输出和中间过程全部打印出来
# 依赖同目录的 staffing_agent.py（逻辑全在那里，这里只负责「边跑边讲」）
# 用法：
#   python3 walkthrough.py                  跑主角那句话，逐站讲解
#   python3 walkthrough.py "需求改成 1300 次"  跑你自己的一句话
#   python3 walkthrough.py --all            主角 + 三个翻车现场 + 四道考考你
#   python3 walkthrough.py -i               交互：一句一句输入，空行退出
import sys, re, json
import staffing_agent as A

def hr(title): print(f"\n{'─' * 6} {title} {'─' * 6}")
def ok(b): return "✓" if b else "✗"
def z(v): return 0 if abs(v) < 1e-9 else v      # 把 -0 显示成 0

def station0():
    hr("第 0 站｜墙上的规矩")
    for k, (n, c, cap) in A.BASE["resources"].items():
        print(f"  {k:<5} 每班 {n:>2} 次  每班 {c:>2}  最多 {cap:>2} 班  → 每次 {c / n:g}")
    print(f"  平时需求 {A.BASE['demand']} 次；合同规则：派遣用满才能叫加急 = {A.BASE['rush_rule']}")
    print(f"  门卫规矩：需求 {A.LIMITS['demand']}，价格变动 ±{A.LIMITS['cost_pct']}%；审批线 {A.APPROVAL_LINE}")

def station1(text):
    hr("第 1 站｜助理 parse：一句话 → 纸条")
    print(f"  进：「{text}」")
    ch = A.parse(text)
    if not ch: print("  四张填空模板都没套上 → 交出空纸条")
    for c in ch:
        print(f"  套上「{ {'demand': '需求 ___ 次', 'cap': '___班 最多 ___ 班', 'cost': '___班 改价'}[c['type']] }」"
              f" → 收据「{c['quote']}」")
    print("  出：" + json.dumps(ch, ensure_ascii=False))
    return ch

def station2(text, ch):
    hr("第 2 站｜门卫 guard：能不能放行")
    for c in ch:
        names = {A.NAMES[k] for k in re.findall("加急|派遣|常勤", c["quote"])}
        q1 = c["quote"] in text
        q2 = len(names) <= 1
        if c["type"] == "demand": q3 = A.LIMITS["demand"][0] <= c["value"] <= A.LIMITS["demand"][1]
        elif c["type"] == "cap": q3 = 0 <= c["value"] <= A.LIMITS["cap"][c["resource"]]
        else: q3 = True
        q4 = True
        if c["type"] == "cost":
            b = A.BASE["resources"][c["resource"]][1]; q4 = abs((c["value"] - b) / b * 100) <= A.LIMITS["cost_pct"]
        print(f"  纸条 {c.get('resource', '需求')} → {c['value']}")
        print(f"    {ok(q1)} 1 真是你说的吗   {ok(q2)} 2 只提到一种班   {ok(q3)} 3 数字合理   {ok(q4)} 4 不用本人签字")
    status, notes = A.guard(text, ch)
    for n in notes: print("  门卫说：" + n)
    print(f"  出：{status}  （ok 放行／ask 反问／reject 拒绝／confirm 要确认）")
    return status

def station3(ch, override):
    hr("第 3 站｜会计 solve：出题、交给求解器")
    m = A.apply(ch)
    if override: m.update(override); print(f"  ⚠ 测试按钮：题目被改成 {override}")
    print(f"  复印件：需求 {m['demand']}，上限 " + "、".join(f"{k} {v[2]}" for k, v in m["resources"].items())
          + f"；BASE 原件仍是需求 {A.BASE['demand']}、常勤 {A.BASE['resources']['常勤加排'][2]}（没被改）")
    r, base = A.solve(m), A.solve(A.BASE)
    R, p = m["resources"], {k: z(v) for k, v in r["plan"].items()}
    print("  求解器 SCIP 给出：" + "、".join(f"{k} {v:g} 班" for k, v in p.items()))
    times = " + ".join(f"{R[k][0]}×{p[k]:g}" for k in R)
    print(f"  核对次数：{times} = {sum(R[k][0] * p[k] for k in R):g}，缺口 {z(r['short']):g}，需求 {m['demand']}")
    print(f"  核对费用：{' + '.join(f'{R[k][1]:g}×{p[k]:g}' for k in R)} = {r['cost']:g}（平时 {base['cost']:g}）")
    return m, r, base

def station4(m, r, base):
    hr("第 4 站｜老师傅 sanity：怪不怪、谁签字")
    flags, who = A.sanity(m, r), A.approver(r, base)
    print("  黄灯：" + ("没有" if not flags else ""))
    for f in flags: print("    ⚠ " + f)
    print(f"  多花 {r['cost']:g} − {base['cost']:g} = {r['cost'] - base['cost']:g}，审批线 {A.APPROVAL_LINE} → {who}")
    return flags, who

def station5(r, base, flags, who):
    hr("第 5 站｜秘书 explain：说成人话")
    print("  " + A.explain(r, base, flags, who))

def trip(text, confirmed=False, override=None, changes=None, show_wall=True):
    print(f"\n{'═' * 40}\n护士长：「{text}」" + ("（已确认）" if confirmed else ""))
    if show_wall: station0()
    ch = changes if changes is not None else station1(text)
    if changes is not None: hr("第 1 站｜跳过：测试按钮 changes= 直接塞纸条"); print("  " + json.dumps(ch, ensure_ascii=False))
    status = station2(text, ch)
    log = {"text": text, "changes": ch, "guard": status}
    if status in ("ask", "reject") or (status == "confirm" and not confirmed):
        print("\n  🔴 急停：门卫没放行，会计不开工。" + ("带 confirmed=True 再跑一次。" if status == "confirm" else ""))
        return log
    m, r, base = station3(ch, override)
    flags, who = station4(m, r, base)
    station5(r, base, flags, who)
    log.update(result=r, flags=flags, approver=who)
    return log

def quiz_penalty():
    hr("考考你 3｜罚金改成 1")
    m = json.loads(json.dumps(A.BASE)); m["shortage_penalty"] = 1
    r = A.solve(m)
    print(f"  方案 {r['plan']}，缺 {r['short']:g} 次 → 什么都不排（最便宜的补法每次也要 4，比罚 1 贵）")

def quiz_no_copy():
    hr("考考你 2｜不复印，直接改 BASE 会怎样")
    saved = json.loads(json.dumps(A.BASE))
    A.BASE["resources"]["常勤加排"][2] = 4           # 模拟「直接在原件上改」
    print(f"  第一句话之后，「平时」变成 {A.solve(A.BASE)['cost']:g}（本该是 606）")
    A.BASE.clear(); A.BASE.update(saved)
    print(f"  恢复原件后，「平时」又是 {A.solve(A.BASE)['cost']:g}")

if __name__ == "__main__":
    args, logs = sys.argv[1:], []
    if not args:
        logs.append(trip("下周三有人请假，常勤最多只能加 4 班"))
    elif args[0] == "--all":
        logs.append(trip("下周三有人请假，常勤最多只能加 4 班"))
        print("\n\n########## 三个翻车现场 ##########")
        logs.append(trip("派遣公司说加急每班 40", show_wall=False,
                         changes=[{"type": "cost", "resource": "派遣", "value": 40, "quote": "派遣公司说加急每班 40"}]))
        logs.append(trip("需求改成 1300 次", show_wall=False))
        logs.append(trip("派遣公司说加急每班 40", confirmed=True, override={"rush_rule": False}, show_wall=False))
        print("\n\n########## 考考你 ##########")
        logs.append(trip("派遣最多只能 10 班", show_wall=False))
        quiz_no_copy(); quiz_penalty()
        logs.append(trip("常勤最多只能加 4 班，需求到 140 次", show_wall=False))
    elif args[0] == "-i":
        while (t := input("\n护士长说（空行退出）：").strip()):
            c = input("要确认的改动算不算？(y/N) ").strip().lower() == "y"
            logs.append(trip(t, confirmed=c, show_wall=False))
    else:
        logs.append(trip(args[0], confirmed="--yes" in args))
    json.dump(logs, open("walkthrough_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n📒 {len(logs)} 张纸条已记进 walkthrough_log.json")
