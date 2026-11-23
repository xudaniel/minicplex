# Trip itinerary agent: change a trip with one sentence

[中文](README.md) | **English**

*“I want to sleep in on day three, nothing before ten.”* Say one sentence and the program rearranges the whole three-day trip, tells you what you lost, and whether the rest of the group needs to agree.

This is a sister project to the [staffing agent](../staffing-agent/README.en.md). The five-station pipeline is unchanged; only the accountant's problem is new: scheduling with time windows. The solver switches from SCIP to CP-SAT, which is built for “these time slots must not overlap.” The city, sights, hours and scores are all invented.

## Run it

```bash
pip install ortools
cd learning/itinerary-agent
python3 itinerary_agent.py --lang en          # the main sentence, station by station
python3 itinerary_agent.py --all --lang en    # plus what the gatekeeper stops and two failures
python3 itinerary_agent.py -i --lang en       # type your own; an empty line quits
python3 -m unittest -v test_itinerary_agent
```

Leave out `--lang en` for Chinese. There is one model and one set of numbers.

## The rules on the wall

- **Three days:** day 1 15:00–21:00 (afternoon arrival), day 2 09:00–20:00, day 3 09:00–12:00 (flight at noon).
- **Ten sights in three districts** (East, Center, West), each with a want-to-go score, a duration and opening hours.
- **Four rules:** 30 minutes between sights; Castle Keep is booked for day 2 at 14:00; on a full day lunch starts between 11:30 and 13:00 and takes an hour (Ramen Alley at noon counts); at most two districts a day.

The original plan scores 60. The Art Museum and the Zoo don't fit (all ten score 71; 71 − 6 − 5 = 60).

## The main sentence, end to end

```
Station 1 | Assistant: {"type": "start", "day": 3, "value": 10}, receipt “day three, nothing before ten”
Station 2 | Gatekeeper: ok
Station 3 | Accountant: Day 1 15:00 Lantern Temple → 17:30 Onsen Street
                        Day 2 09:00 Bamboo Path → 10:30 Skyview Deck → 12:00 Ramen Alley
                              → 14:00 Castle Keep → 18:00 Night Market
                        Day 3 10:00 Seaside Market
Station 4 | Experienced colleague: no flags
Station 5 | Secretary: Want-to-go score 60 (same as the original plan). Approval: your call.
```

Sleeping in costs nothing, yet the whole trip moves: the Seaside Market closes at 13:00, so it slides into day 3's 10:00–12:00 window, and day 2's morning goes to the East-district sights. Every stop gets a ✓ for arriving after opening, finishing before closing and before the day ends, and leaving 30 minutes between stops.

## What the tests cover

| Sentence | Result |
|---|---|
| sleep in on day three, nothing before ten | 60, your call |
| on day two, back at the hotel by 5 pm | 53, the whole group decides |
| we have to go to Universal Studios | ask (not on the list) |
| day five, nothing before ten | reject (only 3 days) |
| must see the Art Museum, and skip the Art Museum | ask (contradiction) |
| let's skip the Castle Keep | confirm; once confirmed 56, whoever paid signs |
| we must see the Zoo | 58 |
| 😈 lunch rule removed | 66, but no time to eat: flagged |
| 😈 two-district rule removed | the Zoo sentence becomes 59 by crossing all three districts: flagged |

Every case runs in both languages and must give the same numbers.

## The model

```
decide:   x[s, d] visit sight s on day d?   st[s, d] arrival time
subject:  arrive after opening; finish before closing and before the day ends
          each visit is an optional interval (duration + 30 min travel); no overlaps per day (AddNoOverlap)
          lunch is one more 90-minute interval starting 11:30–13:00, unless Ramen Alley covers it
          one switch per district per day, at most two on
maximize: want-to-go score first, then earlier starts
```

## Files

| File | Contents |
|---|---|
| `itinerary_agent.py` | the five stations, the narration and the language switch, about 310 lines |
| `test_itinerary_agent.py` | the table above in both languages, `unittest` |
