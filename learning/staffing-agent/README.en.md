# Staffing agent: from one sentence to a plan in five steps

[中文](README.md) | **English**

A head nurse says, almost in passing: *“Someone is off next Wednesday, so regular staff can do at most 4 extra shifts.”*
The program answers the three things she actually wants to know: how to cover the gap, how much more it costs, and who has to sign off.

This folder does not depend on the minicplex solver; it uses Google OR-Tools. It lives here because it shows where an optimization model sits in a real workflow: **the part that understands language listens, the rules decide what may pass, the solver does the arithmetic, and a person signs.**

All numbers belong to an invented clinic. They do not describe any real organization.

## Run it

```bash
pip install ortools
cd learning/staffing-agent
python3 walkthrough.py --lang en          # follow the main sentence station by station
python3 walkthrough.py --all --lang en    # plus three failures and four quiz questions
python3 walkthrough.py -i --lang en       # type your own sentences; an empty line quits
python3 walkthrough.py --lang en "Change demand to 1300 visits"
python3 -m unittest -v test_staffing_agent
```

Leave out `--lang en` and everything runs in Chinese. There is one model and one set of numbers; only the sentences and messages change.

## Five stations

| Station | Function | Receives | Hands off |
|---|---|---|---|
| ① Assistant | `parse` | one sentence | a change request, each item with its source quote as a receipt |
| ② Gatekeeper | `guard` | change request + sentence | ok / ask / reject / confirm |
| ③ Accountant | `apply` + `solve` | an approved change request | plan, cost, shortage |
| ④ Experienced colleague | `sanity` + `approver` | the plan | yellow flags and who signs |
| ⑤ Secretary | `explain` | all of the above | one plain sentence |

Two rules hold the pipeline together:

1. **Each station does one job and trusts only what the previous station handed over.** The assistant never does arithmetic; the accountant never reads the original sentence.
2. **If any station says no, everything after it stops.** Asking one more question is always better than handing over a wrong answer.

Station 1 is a handful of regular expressions standing in for a language model. Swapping in a real model means replacing `parse()` and nothing else: however clever the new assistant is, its notes still go through the same gate.

## The main sentence, end to end

```
Station 2 | Gatekeeper: ✓ you said it ✓ one shift type ✓ in range ✓ no sign-off → ok
Station 3 | Accountant: dispatch 8, regular overtime 4, rush 2
  visits 10×8 + 8×4 + 10×2 = 132 ≥ 130
  cost   50×8 + 32×4 + 75×2 = 678 (usual 606)
Station 4 | Experienced colleague: no flags; 72 extra > 50 → the director signs
Station 5 | Secretary: Plan: dispatch 8 shifts, regular overtime 4 shifts, rush 2 shifts;
  cost 678 (72 more than baseline). Approval: the director.
```

## The model

```
decide:   x[dispatch], x[regular], x[rush] = whole shifts;  short ≥ 0 = visits not covered
subject:  10·x_dispatch + 8·x_regular + 10·x_rush + short ≥ demand
          x_rush ≤ 20·y,  x_dispatch ≥ 8·y,  y ∈ {0,1}   ← contract: fill dispatch before calling rush
minimize: 50·x_dispatch + 32·x_regular + 75·x_rush + 1000·short
```

The shortage costs 1,000 per visit so that, when demand truly cannot be met, the answer is “you are still 12 visits short” rather than just “infeasible”. The penalty must sit well above the most expensive way to cover a visit; set it to 1 and the solver happily schedules nothing at all.

## What the tests cover

| Sentence | Result |
|---|---|
| regular staff can do at most 4 extra shifts | 678, the director signs |
| demand may reach 140 visits | 656, the head nurse signs |
| dispatch agency announced a 10% price increase | 641, the head nurse signs |
| “maybe two or three” (nothing to read) | ask |
| change demand to 1300 visits | reject |
| dispatch can do at most 10 shifts | reject (above the contract) |
| the rush price misread as dispatch | ask (the receipt names two shift types) |
| rush 75 → 40 | confirm; after confirmation 600 |
| same, with the contract rule removed | 520, and a yellow flag |
| regular cap 4 + demand 140 | 753, the director signs |
| shortage penalty of 1 | schedules nothing, 130 short |

Every case runs in both languages and must give the same numbers.

## Files

| File | Contents |
|---|---|
| `staffing_agent.py` | all five stations; `LANG` switches Chinese and English, the model stays the same |
| `walkthrough.py` | runs and explains: prints every station's input, output and the arithmetic to check |
| `test_staffing_agent.py` | the table above in both languages, `unittest` |
