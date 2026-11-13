# 10: Pitfalls and debugging: who fixes what

Benchmarks rank capability and the session log ranks tempo; neither says what
happens the moment a model stumbles. This chapter asks that question with the
same five-month log: how often the models' own errors arise, whether they fix
them alone, and where the human has to step in.

The session database records every tool failure: a command that exits non-zero,
a tool call that misses its target, a fetch that gets blocked, a run that gets
interrupted. Mining the same sessions with the same task-type rules as the
task-type table in [09](09-runtimes.md) (the script is `scripts/mine_errors.py`
in this repo; the fleet, personal and chat categories are omitted here, they are
tooling and admin by nature):

| Metric | Science & manuscripts | Games & creative |
|---|---|---|
| Sessions in the log | 110 | 47 |
| Sessions with at least one failure | 91 (83%) | 32 (68%) |
| Failure events | 781 | 542 |
| - command failed (non-zero exit) | 527 | 275 |
| - agent fumble (mis-called tool) | 183 | 246 |
| - external (fetch blocked, 404, timeout) | 65 | 18 |
| - interrupted (escape) | 6 | 3 |
| Same operation retried before yielding | 92% | 95% |
| Handed back without a retry | 8% | 5% |
| Sessions needing a correction from me | 22 (20% of all) | 17 (36% of all) |

### The science half

Command failures dominate (527 of 781, retried 99.6% of the time): a one-off
analysis script crashes, the model reads the traceback, fixes the line, reruns.
None of that reached me as a decision. Agent fumbles (a stale edit target, an
out-of-range file read, a malformed command line) retried in-turn about 75% of
the time; the rest ended with the model reporting what it could not do, which is the
correct behavior. External failures are mostly publisher sites bot-blocking
scripted fetches (403s). What actually reached me was rarely the crash and
almost always the quality layer: "the subscripts did not render properly and are
still full of underscores", "Figure A needs a rescaled X-axis", "there is still
overlapping text". The model cannot see the rendered PDF; verifying the output
is the human's job, and that is where 20% of science sessions needed me.

### The games half

Fewer sessions, similar failure volume, a different mix. Fumbles were the
games-half signature when this chapter was first written; the newest sessions
(11-06 to 11-08 on occamy-1.0 and sage-a1.5, test-heavy fix passes that rerun
the build after every edit, plus the 11-03 projectile session occamy-1.0 took
over from ornith-1.5) pushed command failures ahead: 275 real failures
against 246 fumbles, retried 99% and 94% in-turn. But the correction
rate runs far higher (36% vs 20%), and the corrections are of a different kind:
"the camera is not centered on the player", "the menu is still broken, there are
no animations", "Sentinel is absolutely broken, no character should have an AOE
(area of effect) as their base attack". A model cannot play its own game. It
writes the code, the code runs, syntax errors are caught and fixed in-turn, and
the experience bugs surface only when a human plays. That is the games loop:
the model's ceiling is not writing code, it is verifying experience.

### By tier and by model

The same failure taxonomy, regrouped by where the model ran: every session with
at least one tool call (361 of the 368, not just the two halves above; the
script is `scripts/mine_failures_by_model.py` in this repo). Failures per 100
tool calls; "fumbles" are the model-attributable kind (mis-called tools).

| Access tier | Sessions | Tool calls | Fails /100 calls | real | fumble | external | abort | Sessions w/ failure |
|---|---|---|---|---|---|---|---|---|
| Pasteur served | 168 | 15,986 | 5.9 | 647 | 218 | 71 | 8 | 77% |
| Ollama Cloud | 107 | 11,489 | 7.0 | 464 | 164 | 178 | 1 | 82% |
| Local rig | 84 | 10,448 | 7.2 | 407 | 311 | 27 | 12 | 68% |
| Free tier | 2 | 41 | 0.0 | 0 | 0 | 0 | 0 | 0% |

The same table, drawn:

![Failures per 100 tool calls, split by kind](charts/failures-by-tier.png)

*The three main tiers as stacked bars: grey = real failures (non-zero exits,
task or environment), red = fumbles (model-attributable mis-calls), amber =
external blocks (bot-walls), dark grey = aborts. The real-failure segment is
nearly the same height on every tier; the differences live in the fumble and
external segments. Segment labels are rounded to one decimal; the free tier
(2 sessions, 41 calls, 0 failures) is in the table only.*

The headline rates separate the tiers less than expected (5.9 to 7.2 per 100).
Split by kind, the real fact appears: command failures land at nearly the same
rate everywhere (3.9 to 4.0 per 100), because a non-zero exit is driven by the
task and the environment, not by which model typed the command. What separates
the tiers is the fumble rate: the served proxy mis-calls tools least (1.4 per
100), Ollama Cloud matches it (1.4), and the local fleet sits at 3.0 (the
11-06 to 11-08 game-fix sessions on occamy-1.0 and sage-a1.5 added a batch of
stale-edit fumbles). And Ollama Cloud's higher
headline is partly not the model's fault: 178 of its failures are external
fetch blocks, the bot-walls of benchmark-season web research.

| Model | Tier | Sessions | Tool calls | Fails /100 calls | Fumbles /100 calls | Sessions w/ failure |
|---|---|---|---|---|---|---|
| medium (served) | Pasteur served | 140 | 14,304 | 5.8 | 1.3 | 79% |
| sage-a1.5 | Local rig | 14 | 4,838 | 6.6 | 2.9 | 100% |
| minimax-m3 (ollama-cloud) | Ollama Cloud | 34 | 3,656 | 5.7 | 1.2 | 82% |
| minimax-m3.1-flash (ollama-cloud) | Ollama Cloud | 19 | 2,860 | 6.8 | 0.6 | 79% |
| occamy-1.0 | Local rig | 13 | 2,733 | 7.8 | 3.4 | 77% |
| glm-5.3-flash (ollama-cloud) | Ollama Cloud | 13 | 2,335 | 8.0 | 2.0 | 100% |
| big (served) | Pasteur served | 26 | 1,647 | 6.6 | 2.2 | 69% |
| flint | Local rig | 10 | 1,119 | 6.2 | 2.4 | 60% |
| kimi-k2.7-code (ollama-cloud) | Ollama Cloud | 7 | 803 | 7.2 | 3.4 | 100% |
| cybertiel-coder-35b | Local rig | 9 | 775 | 9.5 | 2.3 | 78% |
| glm-5.2 (ollama-cloud) | Ollama Cloud | 10 | 564 | 13.7 | 2.7 | 90% |
| kimi-k3.1-pro (ollama-cloud) | Ollama Cloud | 5 | 467 | 4.3 | 1.3 | 60% |
| glm-5.3 (ollama-cloud) | Ollama Cloud | 5 | 393 | 8.1 | 0.5 | 80% |
| mistral-large-4 (ollama-cloud) | Ollama Cloud | 8 | 320 | 7.8 | 1.6 | 62% |
| qwen3.8-27b | Local rig | 17 | 137 | 7.3 | 2.9 | 35% |
| Other models (under 4 sessions each) | mixed | 31 | 1,013 | 8.1 | 3.1 | 61% |

The per-model rates need two honesty flags before any ranking. Denominators
first: qwen3.8-27b's low session-failure share (35%) reflects its chat-era
sessions (137 tool calls across 17 sessions), not excellence. The cleanest
multi-session rate still belongs to the served tier (litellm/medium: 5.8 per
100 over 140 sessions and 14,304 calls; kimi-k3.1-pro's 4.3 is a five-session
sample). On the rig, sage-a1.5 (4,838 calls over 14 sessions, 6.6 per 100)
remains the cleanest local rate, while occamy-1.0 has drifted to 7.8 per 100
over 13 sessions and 2,733 calls as its game-fix sessions piled up. Single-session dominance
second: occamy-1.0's fumbles are 56-of-92 from two game-fix sessions (the
teleport-and-audio session, 29; the projectile-radius session Ornith-1.5
started, 27). Per-model failure rates on this fleet are indicative, not ranked
measurements: one pathological session can dominate a small sample.

### What this teaches

- Mechanical errors are the models' problem, and they mostly solve them alone:
  92-95% of failures are retried in the same turn, and the ones that are not
  usually end with an honest report rather than a hallucinated success.
- Experiential errors are the human's problem, by construction: quality bugs in
  rendered output (papers, figures) and playability bugs in games surface only
  through the person looking at the result.
- The intervention gap between the halves (20% vs 36% of sessions) is the price
  of output you can only judge by experiencing it. A paper's numbers can be
  checked by a script; a game's fun cannot.

(Method: every tool failure recorded in the session database, classified with
the same task-type rules as chapter 09's task-type table; "retried" = the same
operation attempted again before the model handed back; corrections = my next
message matching failure-report wording ("still", "broken", "didn't", and
similar); the tier and model tables rate every session with at least one tool
call, attributed to the session's final model. Rule-based and approximate.)

> **Takeaway:** The models retry 9 in 10 of their own failures, and command
> failures land at nearly the same rate on every tier: what separates tiers is
> the fumble rate. The bugs that reach a human are the ones no machine can see:
> rendered figures on the science half, playability on the games half, and the
> games need far more interventions (36% vs 20% of sessions).

---

*Every abbreviation and term used here is explained in one line in the
[glossary](glossary.md).*
