# Sequential Reciprocal Matching under Extreme Delay and Constrained Information Acquisition

## Abstract / Executive Summary
In sequential matching platforms, participants arrive over time, possess hidden preferences, and have limited patience. The platform must actively decide which pairs to introduce to maximize long-term mutual acceptances. In this proposal, we focus on a heavily constrained environment characterized by a limited daily clarification budget, delayed stochastic feedback, and high opportunity costs for introductions. We propose a hybrid policy that decouples information acquisition from edge valuation. Our preliminary experiments suggest that intelligently allocating the clarification budget (deciding *which* information to acquire) can be more impactful than employing sophisticated probabilistic models for edge valuation. We present empirical evidence that a robust, static matching heuristic outperforms high-variance online learning under severe right-censoring, resulting in a computationally efficient and safe hybrid policy.

## Problem Understanding
The Sequential Matching Problem presents a highly constrained bipartite matching environment:
1. **Incomplete Information:** Participants join with hidden preferences and missing hard-constraint fields.
2. **Limited Clarification Budget:** The platform is constrained by a daily clarification budget of 12 units (clarifying a hard-constraint bundle costs 3 units, while clarifying a single soft field costs 1 unit).
3. **Hard Constraints:** Introducing incompatible participants wastes time and budget.
4. **Delayed Feedback:** Feedback on introductions (dates, second meetings) is stochastic and delayed by up to 7 days.
5. **Opportunity Cost:** Members are unavailable for up to 8 days once introduced, creating significant temporal consequences for matching decisions.
6. **Finite Horizon:** Each matching episode lasts only 60 days.

## Research Question
How should a matching policy allocate limited information-acquisition opportunities and introduction capacity when preferences are partially hidden, feedback is delayed, and introductions incur high opportunity costs?

## Hypothesis
In sequential reciprocal matching with hard constraints, limited clarification budget, delayed feedback, and costly introductions, deciding *which* information to acquire may be as important as deciding *which* feasible pair to introduce. We hypothesize that a computationally cheap, VoI-inspired information-acquisition heuristic paired with a robust greedy matching heuristic will outperform both naive queue-based systems and high-variance probabilistic learning models.

## Proposed Method
Our proposed method is a two-phase daily policy that strictly decouples information acquisition (asking questions) from edge valuation (making introductions).

### Information Acquisition
We introduce a **potential-degree information-acquisition heuristic**. Instead of randomly querying missing constraints or processing members in a FIFO queue, the policy prioritizes members who, if their constraints align, would maximally expand the dense feasible-pair graph.

We define the potential degree <i>D(i)</i> as:
> <i>D(i)</i> =  the number of currently available members <i>j</i> such that the currently observed information does not reveal a hard-constraint conflict between <i>i</i> and <i>j</i>.

The daily clarification budget is greedily allocated to members with the highest <i>D(i)</i>. This serves as a computationally cheap proxy for the potential usefulness of resolving <i>i</i>'s missing constraint information. Our potential-degree heuristic serves as our own problem-specific approximation; while it draws general conceptual inspiration for budgeted information acquisition and value-of-information reasoning from Krause & Guestrin (2009), we explicitly note that our problem is not submodular and the cited work does not prove our heuristic is optimal.

### Matching
For introductions, we use a **greedy matching heuristic that prioritizes feasible pairs using additive soft-field alignment**. The policy constructs the current feasible-pair graph based strictly on known, unviolated hard constraints, and then extracts a maximal matching sorted by simple soft-field commonalities. 

This heuristic was retained because our experiments demonstrated it is robust to missing soft fields, avoids hardcoded public preference weights, lowers variance, and ultimately performed better than our tested probabilistic expected-MSMI scoring models (which suffered from uncalibrated priors and hidden soft-field penalties).

### Sequential Decision Process
The policy operates statelessly across days, strictly using the currently available participants and known constraints. It avoids holding members indefinitely in hopes of a better match, forcing immediate exploitation of known valid pairs.

### Delayed Feedback and Right-Censoring
We implemented and evaluated an online learning component to adapt to preference shifts. However, in this environment, feedback on introductions is delayed by up to 7 days. Furthermore, the episode consists of 60 decision days followed by 40 follow-up days. While the final MSMI evaluation captures outcomes during the follow-up period, the policy itself must cease making introductions at day 60. Therefore, from the perspective of an online learning algorithm attempting to adjust its weights during the active decision period, feedback for introductions made in the final week is heavily right-censored. In our experiments, the online component did not improve performance and drastically increased variance (aligning with findings by Joulani et al., 2013). Therefore, our current policy intentionally favors a robust static heuristic. Adaptive learning remains a possible Round 2 research direction if highly feedback-efficient methods can be developed.

### Exploration vs Exploitation
Given the short horizon, substantial opportunity cost of introductions, and delayed feedback, the current policy prioritizes exploitation. Controlled exploration (e.g., matching low-probability pairs to learn the global preference distribution) remains an open research direction but was deemed too costly under the current 60-day constraints (Johari et al., 2021).

## Experimental Design
We evaluated our approach using the provided local Python simulator across all 6 scenario families (`cold_start`, `delayed`, `development`, `drift`, `shift`, `sparse`). To combat the high stochasticity of date probabilities, we used a rigorous 10-seed evaluation (60 total episodes per variant). The primary evaluation metric is the Mutual Second-Meeting Intention (MSMI) score, supported by secondary metrics: mutual acceptances, coverage, clarification cost, and invalid/disqualification rate.

We conducted a strict component ablation comparing:
1. **Greedy Baseline:** The provided reference implementation.
2. **V4 Policy:** A sophisticated variant featuring probabilistic expected-MSMI scoring and online learning.
3. **Final Hybrid:** Our proposed method using potential-degree asks and greedy heuristic matching.

## Preliminary Results
Our 10-seed, 60-episode final evaluation yields the following aggregate results:

*   **Greedy Baseline:** 0.258 MSMI | 5.63 mutual acceptances | 0.315 coverage | 188.9 ask cost
*   **V4 (Expected-MSMI + Online Learning):** 0.283 MSMI | 4.99 mutual acceptances | 0.312 coverage | 397.2 ask cost
*   **Final Hybrid (Potential-Degree + Heuristic Match):** 0.392 MSMI | 5.62 mutual acceptances | 0.310 coverage | 397.1 ask cost

*Scenario-Level Breakdown (Hybrid):* `cold_start`: 0.50 | `delayed`: 0.45 | `development`: 0.40 | `drift`: 0.40 | `shift`: 0.50 | `sparse`: 0.10.

The potential-degree heuristic dramatically improved MSMI in the `cold_start` scenario (0.50 vs 0.20 for the baseline queue) by efficiently connecting sparse networks. Furthermore, the hybrid policy safely increased the overall MSMI to 0.392 with **zero invalid episodes** and executes an entire 60-day episode in &lt;0.15 seconds for <i>N</i>=200.

## Ablation Plan / Round 2 Research Directions
To further validate and extend this approach, we plan to explicitly model **opportunity cost**. Currently, the hybrid uses greedy immediate feasible-pair selection. However, introductions occupy members for multiple days, meaning matching decisions have deep temporal consequences. Explicitly modeling the future value of waiting (e.g., using a time-decaying wait threshold <i>&tau;</i>) is our primary planned extension.

## Expected Contributions
We contribute an empirically validated demonstration that under extreme constraints and delay, computationally simple information-acquisition heuristics paired with greedy exploitation can substantially outperform complex probability models and uncalibrated online learning. 

## Limitations and Risks
The current hybrid does not solve opportunity cost optimally. By greedily matching immediately, it risks starving the `sparse` variant (as seen by the low 0.10 score) where waiting for better future arrivals might yield higher utility. Furthermore, by prioritizing pure exploitation, the policy is blind to hidden global preference shifts that could hypothetically be learned with a sufficiently long horizon.

## References
1. **Johari, R., Kamble, V., & Kanoria, Y. (2021). Matching while learning.** *Operations Research*, 69(2), 655-681. (Provides theoretical context on the fundamental exploration-exploitation tradeoff when matching under unknown preferences).
2. **Joulani, P., Gyorgy, A., & Szepesvári, C. (2013). Online learning under delayed feedback.** *International Conference on Machine Learning.* (Provides theoretical justification for the variance explosion caused by extreme delay and right-censoring).
3. **Krause, A., & Guestrin, C. (2009). Optimal value of information in graphical models.** *Journal of Artificial Intelligence Research.* (Provides general conceptual inspiration for budgeted information acquisition and value-of-information reasoning, though we make no claim that this paper proves our problem-specific potential-degree heuristic is optimal or submodular).


