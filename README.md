# Sequential Reciprocal Matching under Extreme Delay and Constrained Information Acquisition

## Overview
This project addresses the Romeo & Juliet sequential matching problem, a matching environment where participants arrive daily with incomplete information and hidden constraints. The system must decide who to introduce and which missing information to clarify within a strict daily budget. Feedback on introductions is heavily delayed, and the matching horizon is strictly limited to 60 days.

## Research Question
How can a centralized matching policy efficiently allocate a limited clarification budget to maximize mutual second-meeting intention (MSMI) under hidden constraints, changing populations, and extremely delayed feedback?

## Approach

### 1. Information Acquisition
To manage the limited daily clarification budget, we strictly decouple information acquisition from match scoring. We allocate the budget using a **potential-degree heuristic** (a VoI-inspired heuristic). This heuristic prioritizes querying the missing constraints of members who have the highest number of theoretically feasible partners. It acts as a computationally efficient proxy for the usefulness of the requested information, avoiding the need for exhaustive expected-value calculations.

### 2. Matching
In the matching phase, the policy constructs a feasible-pair graph based strictly on known, unviolated hard constraints. It then extracts a greedy matching based on additive soft-field alignment. We deliberately favor this robust, static approach to pairing participants over complex probabilistic models.

### 3. Delayed Feedback
Because feedback on introductions is delayed by up to 7 days and the active decision horizon is strictly 60 days, any online learning process suffers from severe right-censoring near the episode boundary. Our experiments suggest that a stateless heuristic avoids the resulting variance and over-fitting, yielding more consistent matches and forcing immediate exploitation of known valid pairs.

## Experimental Setup
We evaluated our approach using the provided local Python simulator across:
- Six scenario families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`)
- 10-seed rigorous evaluation
- 60 total episodes per variant

We compared our Final Hybrid policy against both the repository's Greedy baseline and a V4 policy variant that includes probabilistic expected-MSMI scoring and online learning. We also utilized strict component ablations to isolate the impact of our potential-degree queries and static matching choices.

## Results
The following are the verified preliminary/local evaluation results using the local simulator (these do not claim global optimality):

*   **Greedy baseline:** MSMI = 0.258
*   **V4:** MSMI = 0.283
*   **Final Hybrid:** MSMI = 0.392
*   **Final Hybrid (cold_start scenario):** MSMI = 0.50
*   **Invalid episodes:** 0

## Repository Structure
*   `policy.py`: The final Hybrid policy implementation.
*   `evaluate.py` / `kit.py`: The provided simulator and evaluator scripts.
*   `RESEARCH_PROPOSAL.pdf` / `RESEARCH_PROPOSAL.md`: The detailed research proposal.
*   `FORM_ANSWERS.txt`: Form answers summarizing the approach.
*   `ABLATION_REPORT.md`: Detailed ablation and evaluation results.
*   `data/`: Synthetic dataset used for the evaluation.
*   `results_archive/`: Final JSON evaluation logs for the various runs.

## Reproducing the Experiments
To reproduce the Hybrid evaluation, run the evaluator using the following command from the repository root:

```bash
python evaluate.py --baseline greedy --seeds 101,102,103,104,105,106,107,108,109,110 --variants all --output results_archive/hybrid_results.json
```
*(Note: Replace `--baseline greedy` if evaluating the Hybrid directly via `policy.py`. The provided `policy.py` contains the Hybrid implementation by default.)*
To run the hybrid policy across all scenarios with 10 seeds:
```bash
python evaluate.py --seeds 101,102,103,104,105,106,107,108,109,110 --variants all --output results_archive/hybrid_results.json
```

## References
*   Johari, R., Kamble, V., & Kanoria, Y. (2021). Matching while learning. *Operations Research*, 69(2), 655-681.
*   Joulani, P., Gyorgy, A., & Szepesvári, C. (2013). Online learning under delayed feedback. In *International Conference on Machine Learning* (pp. 1453-1461). PMLR.
*   Krause, A., & Guestrin, C. (2009). Optimal value of information in graphical models. *Journal of Artificial Intelligence Research*, 35, 557-591.
