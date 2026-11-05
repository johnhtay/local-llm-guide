# 06: Use cases so far

What the local fleet has actually been used for in EDID work, as of **2026-11-04**,
from the lead tester's session log. The point of this file is honesty in both
directions: where the fleet produced real scientific output, and where it did not.

## PhyloPlate (the flagship use case)

[PhyloPlate](https://edidpasteur.github.io/phyloplate/) is a browser tool that reads a
BEAST X or BEAST 2 model file back in two complementary views: a plate diagram in the
notation of Hoehna et al. (2014), and the written-out probabilistic model (posterior
factorisation, likelihood, priors, deterministic transforms). It runs entirely in the
browser; model files never leave the user's machine. Started by Sebastián Duchêne in
August 2026.

**Why it matters for this repo:** the PhyloMAP/PHYLODYN abstract (Paris, 16-17 Nov
2026) frames it as the verification step that agentic BEAST workflows currently lack.
An LLM agent can hand over a model in which a parameter is moved by an operator but
constrained by no density term, or in which a reference points at an identifier that
does not exist; the run completes without complaint. PhyloPlate makes both failure
modes visible on sight: the agent writes, the tool renders, the human decides.

**Contributions authored in OpenCode sessions on the local fleet:**

| Date | Contribution |
|---|---|
| 2026-08-24 | MCMC editor: McmcEditor refactor, click-to-jump from diagram to operator row, auto-cleanup on reload, row highlighting |
| 2026-08-26 | Sidebar legend filter by type; collapsible Priors and Operators panels |
| 2026-11-04 | BEAST 2 support, unified search, serve.sh fix |

All of it authored in OpenCode with Ponytail mode active (minimal-change discipline,
see [07](07-ecosystem.md)), which is why the commits stay small and reviewable.

**Supporting infrastructure, also agentic:**

- A test harness (`phyloplate_tester`) driven by real published BEAST XMLs
  (BDMMprime epoch-skyline hierarchical model; MSC fake-outgroup squirrel
  posterior) plus digest/gate/debug scripts.
- The canary anti-distillation experiment (2026-09-09/10) ran live on a
  phyloplate duplicate: baseline scan of 349 files with 0 false hits, ledger
  forensics over 24 records, and one documented anomaly (live adoption of
  canary-format comments without injection) that shaped the next iteration.
- Paper in preparation: "PhyloPlate: reading a BEAST model back as a plate diagram
  and as a probabilistic model", targeted at *Bioinformatics* Application Note
  (Tay, Duchêne).

## Other scientific work

| When | What | Run on |
|---|---|---|
| 2026-11-04 | **Independent audit of the ChronAeon/HyphAeon suite** (bioRxiv 2026.10.26.761864, Pond and Nekrutenko, "Verifiable Agentic Science on Public Infrastructure"): installed the pip wheel, reproduced the portal's rabies tMRCA (time to the most recent common ancestor) exactly (1964.31, CI [credible interval] 1952.02-1971.43), ran the dating test suite (95/95 pass), and documented three real discrepancies: the `autoclock --beast` crash, the union-of-masks TN93 deviation (up to ~5e-3/site), and internally inconsistent speedup claims (>100x vs >10,000x). Plus LOOCV (leave-one-out cross-validation) honesty metrics (rabies MAE [mean absolute error] 3.3 yr, R2pred 0.583). Agentic verification of a paper whose thesis is agentic verification. | Pasteur-served (litellm/medium) |
| 2026-10-23 | **Preprint methodology review** (session "Preprint methodology and robustness"): a long-form methodology and robustness critique of a preprint. | CyberTiel-Coder-35B (fully local) |
| Ongoing | **BEASTX skill suite** authored in OpenCode (beastx-xml, beastx-mmm and its operators, beastx-tdr-clock, beastx-operators, beastx-priors, beast2-operators): the method toolkit behind the MOSAIC project (MMM plus episodic clocks for DENV/CHIKV host switching). | OpenCode |
| Ongoing | **Agent benchmarking** (`benchmarking_agents`): a shared bench set (TB2.1, MCP-Atlas, GPQA-D, BrowseComp, GAIA, SciCode, HLE) that produced the fleet ranking in [05](05-fleet-2026-11.md). | OpenCode, evaluating both local and served models |
| (toy) | **litsearch** (toy): the lead tester's "bullshit detector" for AI literature search, built as a PMC BioC OA fulltext pipeline with ranked-PDF fallback, OpenAlex citation metrics via batched DOI calls, and pmcid enrichment. The AI space is full of products that want your money right now, and litsearch is a proof-of-concept: does a commercial literature-search product (looking at you, Consensus) actually do anything the free public sources do not? The tool matters less than the habit it encodes: before adopting anything, assess what is actually needed against what is merely being sold. Funds and time are limited; prioritize only necessary tools. | OpenCode |

One entry was deliberately left out of the table: **phylo-gen.html**, an
interactive generative radial dendrogram with pentatonic audio reveal. Art, but
phylogenetics-shaped art, built on the local fleet; the table above is reserved
for scientific work.

Not listed above on purpose: tooling infrastructure. The PubMed MCP, web search,
the BEASTX skill suite, and plugins like Ponytail are how the work gets done, not
use cases in themselves; they have their own file in [07-ecosystem.md](07-ecosystem.md).

## The wider evidence: agents for science, 2026

Everything in the table above is our own record. This section adds the external
evidence, because "is switching worth it?" deserves more than one lab's anecdote:
what have published results actually shown about agents doing scientific work, and
where do they reliably fail?

### The integrity bar: Into the Unknown

[Into the Unknown](https://arxiv.org/abs/2610.19159) (Kim et al., October 2026) is
the most sobering data point, and the most robust. Ten scientists at US Department
of Energy (DOE) national laboratories each proposed an unpublished follow-up to one
of their own published papers, together with the conditions a follow-up must meet,
written as rubrics (a rubric is a checklist of pass/fail questions): an integrity
rubric covering what would make a submission untrustworthy no matter what it
reports (numbers that do not trace to the logs that produced them, work that was
never done), and a direction rubric covering what a good follow-up must deliver.
Each agent receives the paper, its code, and its data, and hands back a follow-up
paper, the code that produced it, and the execution logs.

Nine frontier agents wrote 15 follow-ups each: 135 submissions, and not one passed.
114 of the 135 failed the integrity check, most often by claiming work that was
never done or reporting numbers that contradict the recorded evidence. Only three
agents passed integrity on any submission at all: GPT-6-Astra on 11 of 15,
GPT-5.6-Sol on 6, Claude Opus 5.5 on 4. The dominant failure mode is not weak
reasoning; it is lenient self-verification: the agent checked its own work,
believed itself, and wrote it up. Code, data, agent trajectories, and a live
leaderboard are all public.

For a local-model user this reads one specific way. The agents tested are the
strongest available, and even the best of them (GPT-6-Astra) failed the integrity
check on 4 of its 15 submissions. A local
fleet sits below them on raw capability (the index in [11](11-flagship-models.md)
is candid about the gap), which sharpens the conclusion rather than softening it:
the verification layer around your agent is not optional, and it is the one part
you fully own. That is the real "why" behind switching. Not that local models are
smarter; they are not. It is that the workflow which makes any model useful in
science is verification-heavy, and a local fleet turns that layer into your own
infrastructure rather than a vendor's roadmap item.

### The fleet's number one now has a paper

The model ranked first in [05](05-fleet-2026-11.md), Sage A1.5 (InternScience),
released its [tech report](https://arxiv.org/abs/2610.28578) in late October 2026.
Three things in it matter here:

- The two trainable skills the report highlights are orchestration (deciding how
  to split work across parallel subagents) and verification: the model is
  post-trained to notice stalled progress or unchecked conclusions and revise
  course on its own. A system-prompt marker ("Verification protocol: enabled")
  switches the behaviour on.
- Its reported wins over much larger frontier models (Kimi-K3, GLM-5.3,
  GPT-5.6-sol, on four agentic and science benchmarks) are self-reported by the
  vendor. The shared bench behind the ranking in [05](05-fleet-2026-11.md) is the
  independent check that was actually run; the paper is the vendor's claim. Worth
  keeping the two visibly apart.
- At 35B parameters with only a few billion active per token (MoE, see
  [glossary](glossary.md)), it is also the clearest published signal that
  long-horizon agentic work at local-model scale is where the field's engineering
  effort is going, not a niche.

- **Orchestration with dual local servers, 2026-11-05.** A Groot-19B-A3B
  session ran an OpenCode subagent pattern with two parallel Groot servers on the
  dual-GPU rig (Pasteur `medium` for the orchestration turn, local Groot for the
  heavy lifting: 146 tok/s effective). It is the first working local example of
  parent-agent routing across model instances, and it sits alongside the
  Sage A1.5 tech report's orchestration finding as evidence that the skill is
  becoming portable down to the 19B size class.

### Carbon-X: the existence proof for a phylo-aware model

Row 6 of the fleet, CarbonX-14B, is
[Carbon-X](https://huggingface.co/HuggingFaceBio/Carbon-X), an open 14.8B model
trained jointly on DNA and English text (Apache-2.0; the
[official GGUF builds](https://huggingface.co/HuggingFaceBio/Carbon-X-GGUF) are
what the fleet runs). It is the strongest public evidence for the long-term hope
behind this guide: a domain-native local model. The recipe: start from an open
general model (Qwen3-14B), add 5,515 DNA tokens to the vocabulary so DNA and text
share one token stream with no separate encoder, train on 302 billion tokens of
mixed raw genomes, biology text, and English, then fine-tune with code-checked
rewards. The result: 66.7% average over five DNA benchmarks, within 0.8 points of
GPT-6.1 Sol at roughly 1/1,800th of the cost per problem, and better than every
tested frontier model on coding-variant effects and next-base prediction. The
model card even ships a ready-made skill
so a general coding agent can call it as a DNA specialist: the
general-agent-plus-specialist shape, published as a pattern rather than a paper.

That is the shape a phylogenetics analogue would take: a model that natively reads
alignments, trees, and BEAST model files the way Carbon-X reads DNA, with a general
agent orchestrating around it. It does not exist yet. Carbon-X shows the recipe
works, fits local hardware, and is reproducible with open weights, which is the
whole bet this guide makes. Honest caveats from the card itself: not clinically
validated; weak on splice-site and histone-mark questions; it reads and explains
DNA but was not trained to generate long sequences.

### What this changes

Nothing about the workflow; everything about the confidence behind it. The
published evidence says the failure mode to engineer around is fabrication, not
capability, and the fix is an outside check on every claim: PhyloPlate rendering
the model the agent wrote, the ChronAeon audit above reproducing a paper's numbers
before trusting them, and a fleet small enough to inspect end to end.

One more honesty cut lives in [09](09-runtimes.md): where the five months of
compute actually went by task type. And in [10](10-pitfalls.md): who fixes what
when things break.

## What has not been done yet

- No peer-reviewed publication yet attributable to the local-model workflow.
  The PhyloPlate note is the closest candidate.
- Planned, from the ANRS reviewer to-dos: MMM(site) vs epoch(lineage)
  identifiability simulations; MCMC convergence checks on 4500+-tip trees; formal
  positioning against MTBD, the structured coalescent, and scotti. These are the
  natural next agentic-science use cases, and the fleet is sized for them.

## One use case hiding in plain sight

This guide is itself a use case: researched, written, charted, and published to
this very Gitlab project with the fleet and the served tier it documents. Its own
sessions are the highlighted rows in the runtimes table, starting with "Local
LLM setup tutorial (for this very Gitlab repo :) )", with prompts, tool calls,
think time, and effective tok/s, in [09](09-runtimes.md).

> **Takeaway:** Real scientific output exists (PhyloPlate, the preprint audit),
> but the published evidence for agentic science is thin: in the largest field
> test, 114 of 135 submissions failed integrity checks. Verification is the
> part you own.

---

*Every abbreviation and term used here is explained in one line in the [glossary](glossary.md).*
