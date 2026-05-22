Multi-Model Scheduling Design

Goal
- Provide an architecture for realistic full-day scheduling using multiple models and rule-based components.

Proposed components

1. Task Type Classifier (supervised)
- Input: task text (and context)
- Output: category label (ritual, commute, meeting, focused-work, break, exercise)
- Use: informs downstream duration priors and scheduling rules

2. Duration Predictor (regression)
- Input: task text, task type, user profile
- Output: duration in minutes (mean + uncertainty)
- Use: assign concrete time slots
- Short-term: implement a rule-based fallback mapping common keywords to durations

3. Priority/Weight Model (optional supervised)
- Input: task text, context, deadlines
- Output: weight or priority score used to split available time

4. Scheduling Engine
- Inputs: list of tasks with durations/weights, available window
- Behavior: allocate slots, insert fixed rituals, respect weights/durations
- Output: persisted schedule rows + API response with start/end/duration

5. RL Agent(s)
- Use RL to optimize allocation inside flexible blocks (e.g., how to sequence concentrated work segments)
- Could be single agent or multiple agents specialized by task type

Data & Iteration Plan
- Phase 1: rule-based durations + weights; collect logs of user adjustments
- Phase 2: train supervised duration/priority models from collected data
- Phase 3: introduce RL agent(s) for optimization within flexible blocks; evaluate A/B

Implementation notes
- Keep modules small and testable: `nlp/` for extraction/classification, `models/` for trained predictors, `scheduler/` for allocation logic, `backend/` for API.
- Persist both inputs and outputs to enable later supervised training (store task text, assigned durations, user edits).

Deliverables
- Short-term: rule-based duration predictor + per-task durations in API (implemented)
- Mid-term: a simple supervised duration predictor trained on collected edits
- Long-term: RL agents specialized per task type and joint scheduler

Metrics
- Estimation accuracy (duration error)
- User acceptance (manual edits rate)
- Productivity improvement (task completion / reward proxy)
