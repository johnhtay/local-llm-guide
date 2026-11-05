# 06: What we actually use this for

The setup is not the point; the work is. Here is what the lab has actually done
with locally run models so far (November 2026).

## PhyloPlate: the flagship

- **What it is:** a web page that reads a BEAST model file (the XML the lab feeds
  to BEAST) and draws it back two ways: as a picture (a "plate diagram") and as
  the model written out in equations. You drop your XML on the page; nothing is
  uploaded anywhere.
- **Why it matters:** AI assistants now write these model files, and sometimes they
  write files with real mistakes: a parameter that the math changes but nothing
  constrains, or a reference to something that does not exist. BEAST runs anyway
  and reports nothing. PhyloPlate makes such mistakes visible at a glance.
- **What the local models contributed:** the MCMC editor (August), sidebar filters
  (August), and BEAST 2 support plus unified search (November 4).
- **Output:** a paper in preparation (Bioinformatics short format, with Sebastián
  Duchêne) and a talk at the PhyloMAP/PHYLODYN meeting in Paris, 16-17 November
  2026.

## Other scientific work

- **A paper check (November 4):** an AI agent independently re-ran the
  computations behind a published preprint (about AI-run science, fittingly),
  reproduced its headline numbers exactly, then found three real mistakes,
  including a crash in the authors' own tool. Run on the lab's Pasteur-served
  model.
- **A preprint review (October 23):** a fully local model (CyberTiel) wrote a
  long methodology-and-robustness critique of a preprint.
- **litsearch (a proof-of-concept):** a homemade fact-checker for AI search products. Many
  companies sell AI tools for searching papers, and they all want your money
  right now. litsearch is a proof-of-concept: does the paid product do anything
  the free public sources (PubMed and friends) do not? The tool itself matters
  less than the habit it teaches: the AI space is full of people who want your
  money, so always check what you actually need before paying for anything. We
  have limited funds and limited time, so we only keep the tools that are truly
  necessary.
- **The BEASTX skills (ongoing):** instruction packs that let any local model
  write and debug BEAST model files correctly.
- **Model testing (ongoing):** the same quiz given to every candidate model; that
  is how the recommendations in [05](05-models.md) were chosen.

## Honesty

Games and small apps are the sessions I like to show people, but they are only
about 11% of the real compute time. About 40% goes to keeping the rigs and tools
running (launchers, updates, breakage fixes), and about 37% goes to science.
The games are capability testing: they are how the models got fast and reliable.
The science so far is concentrated in PhyloPlate, the paper check, and the
reviews.

When something breaks, the models fix most of their own mistakes before I ever
see them (about 9 in 10 failures get retried and solved in the same turn). The
bugs that do reach me are the ones a machine cannot see: a figure whose axis is
wrong, a game whose camera drifts. I look and play; the models fix. The log
also says this: when a command genuinely fails (the computer returns an error),
it fails at about the same rate on every model; the task and the environment
cause those. What differs between models is how often they fumble, meaning
reading the wrong file or editing the wrong place.

And it is not just our own log. In the largest published test of AI-run science
so far, nine frontier agents each wrote 15 research follow-ups: 135 submissions,
and not one passed. 114 failed basic integrity (claiming work that was never
done, or numbers that contradict the logs); the best-scoring agent,
GPT-6-Astra, still failed 4 of its 15. The typical failure was not weak
reasoning but the agent believing its own checks. So verification stays with
you, whoever runs the model.

Full detail with dates and numbers: [../06-use-cases.md](../06-use-cases.md)
(use cases) and [../09-runtimes.md](../09-runtimes.md) (time and error totals)
in the advanced track.

---

*Unfamiliar words? One-line explanations in the [glossary](glossary.md).*
