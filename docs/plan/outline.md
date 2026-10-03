# Problem outline — qmind-step-detector (established in a prior turn)

Labels: [Verified] = read in code or executed. [Inference] = reasoning, untested. [Unverified] = depends on outside facts not checked.

## 1. The problem
README: "Geotab's GO device sits in a car at a random angle. Before its accelerometer data means anything, it has to work out which way is down."
README: "counting steps with a phone, however it's held, walking or running."
Goals: (1) classify still/walking/running, (2) count steps within 3% (README.md:92), (3) A/B/C experiment showing orientation correction is what makes the model generalise, (4) live demo + pitch.

## 2. Pipeline as built
| Stage | Code | Today |
|---|---|---|
| Find down | orientation.py:10 gravity_lowpass | exponential average, tau_s=1.0 |
| Gyro option | orientation.py:21 gravity_complementary | [Verified] never called; server.py and train.py never read gyro |
| Split motion | orientation.py:35 vertical_horizontal | vertical = along - |g|; horizontal is a scalar magnitude |
| Frequency | steps.py:12 cadence_hz | biggest FFT peak in 1-4 Hz, swap to half-frequency peak if > 0.4x max |
| Classify | steps.py:42 classify | rule: v_std<0.4 STILL; cadence>2.35 or v_std>5 RUNNING; else WALKING |
| Count | steps.py:49 detect_steps | thr 0.6*std; min gap 0.4 s walking / 0.28 s running |
| Live | server.py:33 state() | 8 s buffer, 2 s feature window, 4 s detection window, dedup by sample index |
| Experiment | train.py | RandomForest trained on A raw xyz / B magnitude / C vert+horiz; leave-one-placement-out and leave-one-person-out |

## 3. Measurements (synthetic data via scratchpad/harness.py which replays simulate.py-style signals through server.ingest/state)
- walk 60s: 108/108; run 60s: 168/167; walk30-run30-walk30: 192/192; still 20s: 0 steps, always STILL. [Verified]
- FFT bin spacing for 2 s window at 100 Hz: 0.5 Hz. [Verified]
- Running with stride asymmetry 1.0 (pocket leg): 204/286 windows labelled WALKING with cadence 1.5 Hz. [Verified]
- Running signal processed in one pass with detect_steps(v, "WALKING"): 84 of 167 steps. [Verified]
- Dashboard polling every 5 s instead of 0.2 s: 84 of 108 steps counted. [Verified]
- train.py on synthetic 4 people x 3 activities x 2 placements, leave-one-placement-out: A 89%, B 100%, C 94%. [Verified]
- [Inference] Simulator is too easy (fixed angle, perfectly regular steps, clean spikes); near-perfect numbers do not transfer.

## 4. Problems, most serious first
1. A/B/C may not show what the pitch says: B (magnitude) is also orientation-invariant and beat C on synthetic data. Unfair comparison: C keeps h_std, A and B drop it (train.py:47-48). [Verified]
2. Cadence resolution 0.5 Hz: spm jumps by 30; 2.35 Hz threshold sits between bins. [Verified]
3. Half-frequency rule can halve running cadence when pocket-leg asymmetry puts a peak at ~1.4 Hz inside the 1-4 Hz band -> run labelled WALKING. [Verified synthetic]
4. Wrong state breaks counting: WALKING min_gap 0.4 s caps at 2.5 steps/s, running misread as walking loses ~half the steps in a one-pass count. Live server happened to be right (overlapping windows) — not investigated. [Verified]
5. Steps are only counted when the dashboard polls GET /state (server.py:67-69). Closed tab / throttled tab loses steps. [Verified + Inference]
6. No accuracy check exists: nothing reads steps.txt; the 3% target cannot be measured. [Verified]
7. Trained model unusable in app: train.py never saves a model; labels walk/run/still vs WALKING/RUNNING/STILL. [Verified]
8. Timestamps ignored: server and train.py assume exactly 100 Hz. [Verified]; whether Sensor Logger delivers 100 Hz [Unverified].
9. Fragile loading: folder `brett_still` -> ValueError in train.py:55; any loose file in data/ would crash load(). [Verified / Inference]
10. Smaller: ingest may double-count if both totalacceleration and accelerometer stream [Unverified]; gethostbyname(gethostname()) may print 127.0.0.1 [Inference]; README clone URL points to James-Cawse/ but repo is bigb05092007/qmind-step-detector [Verified].

## 5. Pairs (README.md:87-92)
Orientation (orientation.py), Frequency (steps.py cadence_hz), ML (train.py), Accuracy (steps.py detect_steps). Plus demo/server.

## 6. Open questions
1. Does real data match synthetic? Needs recordings (data/ is empty).
2. What sample rate and streams does Sensor Logger send?
3. If B >= C on real data, how is "orientation matters" argued?
