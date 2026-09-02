# Theoretical Foundations: Why LLMs Fail at Spatial Synthesis

## 1. The Core Scientific Diagnosis

Autoregressive Large Language Models (LLMs) operate by sampling tokens from a 1D probability distribution:
$$P(w_t \mid w_1, w_2, \dots, w_{t-1})$$

When an LLM is asked to generate 2D vector graphics (such as SVG code), it suffers from four foundational structural bottlenecks:

### A. Dimensionality Mismatch (1D Sequence vs. 2D Euclidean Space)
* **The Mechanism:** Transformers do not maintain an internal 2D Euclidean coordinate buffer in latent memory. 
* **The Failure:** When emitting coordinate attributes (e.g., `<rect x="504" y="720" ... />`), the model samples numbers based on token co-occurrence probabilities in code corpora rather than computing spatial intersections, bounding-box clearances, or support surfaces.

### B. Formal vs. Functional Linguistic Competence
* **The Research:** Mahowald, Ivanova, et al. (*Trends in Cognitive Sciences*, 2024, [arXiv:2301.06627](https://arxiv.org/abs/2301.06627)) demonstrated that LLMs decouple **formal linguistic competence** (mastery of syntax, grammar, tag nesting, CSS formatting) from **functional competence** (world knowledge, intuitive physics, spatial reasoning, and situation modeling).
* **The Failure:** An LLM can easily generate 100% syntactically valid SVG code while simultaneously producing an impossible physical state (e.g., tables floating in air, plants inside window glass, inverted z-indices).

### C. The "Execution-Spatial Gap" & Blind Coordinate Sampling
* **The Research:** Diagnostic benchmarks (*SVGEval*, 2024; *Reason-SVG*, Zhang et al., 2024; *Real-3DQA*, 2024) prove that code being syntactically executable is uncorrelated with spatial correctness. 
* **The Failure:** Without an externalized reference frame, models suffer from "blind coordinate sampling," guessing numbers locally that conflict globally.

### D. The "Quarter of Intelligence" Ceiling
* **The Research:** On the *Training Data* podcast (Aug 2026), reinforcement learning pioneer Rich Sutton (author of *The Bitter Lesson*) and Khurram Javed noted that current static LLMs represent roughly **a quarter of intelligence**—the linguistic mapping quarter.
* **The Failure:** The missing 75% comprises state tracking, perception-action loops, and physical grounding in an active environment. When prompted without environmental constraints, LLMs hallucinate geometry out of frozen text priors.

---

## 2. Benchmark & Prior Art Index

| Benchmark / System | Paper / Citation | Core Finding & Relevance |
|---|---|---|
| **Dissociating Language and Thought** | Mahowald, Ivanova et al. (*Trends in Cognitive Sciences*, 2024) | Foundational proof that grammatical competence in LLMs does not equal real-world common sense or spatial modeling. |
| **Reason-SVG (Drawing-with-Thought)** | Zhang et al. (*arXiv*, 2024) | Proved that intermediate symbolic scratchpads (canvas planning $\rightarrow$ coordinate computation) are necessary to eliminate vector syntax-spatial disconnects. |
| **LayoutGPT** | Feng et al. (*NeurIPS*, 2023) | Showed that formatting spatial planning into structured CSS code schemas drastically outperforms natural language descriptions for 2D/3D layouts. |
| **DirectLayout** | *NeurIPS*, 2024 | Demonstrated that multi-object indoor scene generation requires explicit inequality clearance constraints to prevent physical collisions. |
| **FloorplanQA & PlanQA** | *OpenReview*, 2024 | Proved that unconstrained LLMs fail at indoor metric and topological reasoning (containment, path clearance, wall alignments). |
| **Mind's Eye** | Liu et al. (*DeepMind / MIT*, 2023) | Demonstrated that language models require external neuro-symbolic physics grounding to make accurate spatial predictions. |

---

## 3. How the Construction Site Metaphor Bridges the Gap

The `spatial-svg-architect` skill solves the LLM world-model deficit by converting an unconstrained generative search into a **deterministic compilation pipeline**:

1. **Replaces Token Guessing with Arithmetic:** Anchoring the origin line ($y_{\text{datum}} = 720\text{px}$) and metric multiplier ($288\text{px} = 1.00\text{m}$) turns spatial design into deterministic arithmetic formulas.
2. **Topological Build DAG:** Aligns SVG DOM paint order ($z$-index) with physical assembly dependencies ($Shell \rightarrow Fenestration \rightarrow Light \rightarrow Furniture \rightarrow Foreground$), making collision bugs structurally impossible.
3. **Environmental Invariants:** Binds all secondary visual elements (cast shadows, catenary cables, curtain billows, steam plumes) to explicit global vector fields ($\vec{g}$, $\vec{L}$, $\vec{W}$).
