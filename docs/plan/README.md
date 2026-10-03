# qmind-step-detector — integrated execution plan

Generated 2026-10-03 from two adversarially-verified workflows (28 agents, 0 errors) plus orchestrator additions where marked.

| Document | What it holds | Verification status |
|---|---|---|
| `python-tasks.md` | **Track A — Python pipeline**: 57 tasks T01…T44 + G01…G10, 13 waves, full specs with acceptance commands and expected numbers, goal chains, risks | Every task adversarially verified against the code by a per-area verifier; critic + gap verifier pass |
| `ios-workarounds.md` | **Track B research**: 16 surviving / 11 refuted mechanisms for live sampling with the phone locked in a pocket, recommended architecture, validation protocol, evidence appendix | Every claim fetched and quoted; developer reports labelled separately from Apple statements |
| `ios-tasks.json` | **Track B tasks** IOS-BG-01…08 (keep-alive, lifecycle, feedback, fallbacks, acceptance run) | Produced by the verified synthesis |
| this file, section 3 | **Track B port tasks** IOS-PORT-01…08 (Swift maths package, oracle tests, app shell, TestFlight) | **Drafted by the orchestrator from verified facts; NOT adversarially verified.** Run a verify pass before assigning if time allows. |
| `python-tasks.json` | machine-readable Track A tasks, waves, dropped, concerns | — |
| `decisions.md`, `facts-ios-sensorlogger.md`, `outline.md` | decisions made with the user; verified Sensor Logger / CoreMotion facts; the original problem outline | — |

Evidence labels throughout: **Verified** (read in code / executed / fetched), **Inference** (reasoned, not run), **Unverified** (depends on a real phone or an unreachable source).

---

## 0. Scope change (user decision, 2026-10-03, after the workflows ran): the on-board iOS app replaces the server demo

The iOS app is the **only** demo path. `server.py`, `dashboard.html` and `simulate.py` are no longer a product; they stay in the repo as legacy tooling. The Python pipeline (`orientation.py`, `steps.py`, `train.py`, the new fixtures/evaluation scripts) remains the **reference implementation, trainer and test oracle** for the Swift port. Track C below is therefore void.

**Dropped from Track A (18 tasks, all server/dashboard/simulator work):** T12 T13 T14 T15 T16 T17 T18 T19 T20 T21 T24 T25b T26 T27 T40 G04 G05 G07, plus the optional DEV-01. Their specs stay in `python-tasks.md` for the record; ignore their rows in the wave tables.

**Dependencies adjusted for the 39 remaining Track A tasks (computed from `python-tasks.json`, then checked against the wave tables):**
- T31 "min-gap from cadence": files → `steps.py` only (drop `server.py`); depends_on → T08, T28 (drop T12). Its acceptance keeps the offline `count_steps` numbers; delete the server part.
- T41: depends_on → T35 (drop T40).
- G06: depends_on → T38, T10b (drop T15).
- G10: depends_on → G08, T44 (drop G05); remove the "cellular check" note.
- Everything else is unchanged. No remaining task touches `server.py`, `dashboard.html` or `simulate.py`.

**Added (drafted, not verified):**
- **D-01 README: demo is the iOS app** — Problem (Verified): README.md §6 (lines 94-107) describes the server + hotspot demo and §1 step 3 tells people to run `server.py`/`simulate.py` as the setup check. Change: rewrite §6 around the iOS app (TestFlight install, Guided Access fallback runbook link to `docs/demo-runbook.md` from IOS-BG-07), move the `server.py`/`simulate.py` instructions to a short "Legacy: laptop dashboard" subsection, keep the pitch beats. Acceptance: `grep -c 'TestFlight' README.md` ≥ 1; `grep -c 'Legacy' README.md` = 1; no instruction in §1 or §6 requires `server.py`. Depends on: IOS-BG-02 (so the README names the keep-alive that measured best), T43 (README serialisation). Size S. needs_human: no.

**Goal 4 definition of done** becomes IOS-BG-08 alone (locked-in-pocket walk within 5% of manual count on every team phone; the Guided Access kiosk IOS-BG-07 is the fallback, not the server).

**Cross-track table (section 4):** read Track C as empty; the "Install cloudflared" item is void.

**Open decision 1 in section 7 is answered** (replace). Decisions 2 and 3 remain.

---

## 1. Objective and definition of done

Four goals (README.md:1-16, outline.md §1):

| Goal | Done when |
|---|---|
| 1. Classify still / walking / running | `python3 tests/run.py` exits 0; `evaluate.py` prints `label accuracy: 100.0%` on synthetic (T10b after T28); trained model loads in `steps.classify` and is visible on `/state` (T38, G06, G07) |
| 2. Count steps within 3% | `python3 evaluate.py --data data_synth` ends `… 24/24 recordings within 3%` (T09); the same gate on **real** recordings pasted into README §7 (G10) |
| 3. A/B/C shows what orientation buys | `train.py` prints per-fold accuracy and confusion for A/B/C/D (T34, T35); README states what B ≥ C would mean (T41) |
| 4. Live demo | (a) **on-board iOS app**: locked-in-pocket walk within 5% of manual count on every team phone (IOS-BG-08); (b) **fallback**: `server.py` behind a public URL (G05), counting without a dashboard poll (T12), `./check.sh` prints `CHECK OK` (G08) |

Architecture decision (decisions.md §5-6): the on-board iOS app is the target; the Python pipeline is the reference implementation and the test oracle; training and A/B/C stay on the laptop; the server demo is the fallback for the day.

---

## 2. Rules for every agent (and every human taking a task)

1. One task per branch `task/<id>`; touch only the task's listed files. Need a change elsewhere → stop and report.
2. Run the task's acceptance command before finishing; paste its output verbatim.
3. Task turns out wrong (problem absent, number doesn't reproduce, dependency landed with other names) → stop and report; never widen.
4. Label every claim Verified / Inference / Unverified.
5. Expected numbers assume numpy 2.4.6 (RNG + QR sign conventions). State your numpy version if a number is off. **Add `numpy>=2,<3` to requirements.txt inside T37's requirements edit** (python-tasks.md risk 9; no separate task).
6. `needs_human=true` tasks: the human part (phone, Mac, Xcode) happens first; the agent part runs after it is committed.
7. iOS background measurements: launch from the Home screen with **no debugger attached** (Xcode attached masks suspension — ios-workarounds.md §3.3).

---

## 3. Track B — Swift port tasks (IOS-PORT-01…08) — DRAFTED, NOT VERIFIED

Facts these rest on (facts-ios-sensorlogger.md): raw total acceleration is `CMMotionManager.startAccelerometerUpdates → CMAccelerometerData.acceleration` in **G** (×9.80665 to match Python) [Verified]; CMMotionManager caps at 100 Hz, 40/100 Hz honoured exactly [Verified]; Accelerate/vDSP is Apple-only, so the package needs its own DFT [Verified]; `swift test` runs XCTest on Ubuntu [Verified]; no Swift toolchain in the agent container [Verified]; G09 (`oracle_dump.py`) writes `oracle/<name>.json` with `acc` (6 decimals), `g`, `vertical`, `horizontal`, `hops` (end index + 7 features + state), `count`, `states` [spec in python-tasks.md]. Numpy's `rfft` of N=200 gives bins 0.5 Hz apart; zero-padding to 256 would change bins and break the oracle, so use a direct DFT at the exact N the Python uses (post-T28 Python zero-pads 8× — the port must mirror whatever `steps.spectrum` does at the time the oracle is generated).

Hard constraint (all IOS-PORT tasks): raw accelerometer only; `CMDeviceMotion.gravity/userAcceleration`, `CMPedometer` are comparison columns, never inputs to the detector.

### IOS-PORT-01 Swift toolchain for the agent container
- Problem (Verified): `swift: command not found` on Ubuntu 24.04 x86_64; agents cannot run `swift test`.
- Change: install the current Swift release for Ubuntu 24.04 (swift.org tarball or `swiftly`) under `/opt/swift`, add to PATH via a `tools/swift-env.sh` the other tasks source; create `ios/StepCore` with `swift package init --type library` and one trivial XCTest.
- Acceptance: `source tools/swift-env.sh && swift --version` prints a version line; `cd ios/StepCore && swift test` exits 0.
- Depends on: none. Size S. needs_human: no. Evidence: Verified (absence) / **Unverified whether the environment's network policy allows the download** — if blocked, this task reports that and IOS-PORT-02…05 become Mac-only (`needs_human=true` for their acceptance).

### IOS-PORT-02 StepCore: orientation (gravity low-pass + vertical/horizontal split)
- Problem (Verified): no Swift implementation of `orientation.py:10-42` exists.
- Change: `Sources/StepCore/Orientation.swift`: `struct GravityLowpass(fs: Double, tauS: Double = 1.0)` with `alpha = 1/(1 + tauS*fs)`, seeded from the mean of the first `fs` samples exactly like `orientation.py:15-17`; `func verticalHorizontal(acc: [SIMD3<Double>], g: [SIMD3<Double>]) -> (vertical: [Double], horizontal: [Double], down: [SIMD3<Double>])` mirroring `orientation.py:38-41`. Pure Swift; **no `import simd`, no Accelerate** (stdlib `SIMD3<Double>` only, so it builds on Linux).
- Acceptance: `swift test --filter OrientationTests` loads `oracle/walk_10s.json` and `oracle/run_10s.json`, runs the Swift pipeline on `acc`, and asserts `max |vertical_swift - vertical_oracle| < 1e-5` and the same for `horizontal` and each `down` component (oracle is stored at 6 decimals, hence 1e-5 not 1e-9). Exit 0.
- Depends on: IOS-PORT-01, G09. Size M. needs_human: no. Evidence: Inference (spec mirrors verified Python).

### IOS-PORT-03 StepCore: spectrum, cadence, features
- Problem (Verified): no Swift equivalent of `steps.spectrum / cadence_hz / features` (steps.py:6-39).
- Change: `Spectrum.swift`: `hanning(n)` as numpy's symmetric window `0.5 - 0.5*cos(2πk/(n-1))`; a direct real DFT (`O(N²)`, N = window length after whatever padding `steps.spectrum` uses at oracle time) returning `(freqs, amplitude = |X|/N)` for bins `0…N/2`; `cadenceHz` reproducing the Python rule **as it is in `steps.py` when the oracle was generated** (read the committed `steps.py`; after T28 that is 8× zero-pad and ratio 0.6); `features(vertical, horizontal) -> [String: Double]` with the seven keys of `steps.features`.
- Acceptance: `swift test --filter SpectrumTests`: for every hop in `oracle/mixed_30s.json`, each of the 7 feature values matches the oracle within `1e-5` absolute or `1e-6` relative, and `cadence_hz` matches exactly. Exit 0.
- Depends on: IOS-PORT-02. Size M. needs_human: no. Evidence: Inference.

### IOS-PORT-04 StepCore: classify rule, peak detection, one-pass counter
- Problem (Verified): no Swift equivalent of `steps.classify / detect_steps` and T08's `count_steps`.
- Change: `Steps.swift`: `classifyRule(features)` (thresholds read from one `Thresholds` struct so a later model/threshold change is one edit); `detectSteps(vertical, state/minGap)` mirroring `steps.py:49-62` **as modified by T31** (min-gap from cadence); `countSteps(acc) -> (count, states)` mirroring T08 exactly (hop 20 samples, warm-up 300, 4 s detection window, dedup 25/20 samples — see python-tasks.md T08).
- Acceptance: `swift test --filter CountTests`: for `walk_10s`, `run_10s`, `mixed_30s` the Swift `count` equals the oracle `count` and the `states` array equals the oracle `states` element-for-element. Exit 0.
- Depends on: IOS-PORT-03. Size M. needs_human: no. Evidence: Inference.

### IOS-PORT-05 StepCore: streaming engine driven by timestamps
- Problem (Verified): the app receives samples one at a time with `CMAccelerometerData.timestamp` (seconds since boot) and must not assume 10 ms spacing (Apple: "always check the timestamps"; Sensor Logger author: sampling is never perfectly even).
- Change: `StepEngine.swift`: `mutating func push(t: Double, a: SIMD3<Double>)`; keeps an 8 s ring buffer, measures the rate from timestamp deltas over the last 2 s, resamples to 100 Hz by linear interpolation when the measured rate deviates > 5% (mirrors T17/T18/G02), runs the hop logic of IOS-PORT-04 every 20 input samples, and publishes `(count, state, cadenceHz, down, tilt, measuredHz, spectrum)`. Splits windows on gaps > 2 samples (no interpolation across a gap).
- Acceptance: `swift test --filter EngineTests`: (1) feeding `oracle/mixed_30s.json` `acc` with timestamps `i*0.01` gives the same final `count` and `states` as IOS-PORT-04; (2) the same samples with timestamps `i*0.0095` (105 Hz) give a count within 3% of `true_steps`; (3) a 0.5 s gap inserted mid-stream produces exactly one gap event and no crash. Exit 0.
- Depends on: IOS-PORT-04. Size M. needs_human: no. Evidence: Inference.

### IOS-PORT-06 App shell: RawAccel → StepEngine → UI, with a raw CSV log for field oracle checks
- Problem (Verified): nothing runs StepCore on a phone; the Python pipeline can only be compared with the app if the app logs what it saw.
- Change: `ios/StepDetector` SwiftUI app: uses `RawAccel` (IOS-BG-01/03/04) → `StepEngine`; screen shows steps, state, cadence (spm), measured Hz, tilt / down vector, live spectrum, lifecycle log. **Logs every raw sample** to `Documents/session_<date>/Accelerometer.csv` in the Sensor Logger layout `time,seconds_elapsed,z,y,x` in **m/s² total acceleration** (so `train.load`/`evaluate.py` can read it as a `TotalAcceleration.csv`-style folder once renamed) plus `steps.txt` from the manual count.
- Acceptance (needs a phone + Mac): a screen-on, hand-held walk of 100 manually counted steps: app count within 3%; then copy the session folder to `data_field/<name>_walk_hand/`, rename the CSV `TotalAcceleration.csv`, run `python3 evaluate.py --data data_field` — Python count equals the app count ±1 step. Any larger gap is a port bug (the oracle tests should have caught it) or a timestamp handling difference (IOS-PORT-05).
- Depends on: IOS-PORT-05, IOS-BG-03, IOS-BG-04. Size M. needs_human: yes. Evidence: Inference.

### IOS-PORT-07 TestFlight internal build
- Problem (Verified from decisions.md §6): paid developer account and Mac exist; nothing is set up.
- Change: bundle id, signing, App Store Connect app record, internal tester group with every team member; archive and upload; everyone installs via TestFlight. Developer Mode on each iOS 16+ phone (Unverified requirement, confirm on device).
- Acceptance: every team iPhone runs the current build installed from TestFlight (not Xcode); a 2-minute screen-on walk counts within 3% on each.
- Depends on: IOS-PORT-06. Size S. needs_human: yes. Evidence: Unverified (process steps).

### IOS-PORT-08 Threshold freeze and oracle refresh gate
- Problem (Inference): thresholds (`tau_s`, 0.4/2.35/5, half-rule ratio, min-gap) will change in Track A (T28, T31, T39, G10). A port that froze early drifts from the reference.
- Change: `ios/check.sh`: `python3 oracle_dump.py && (cd ios/StepCore && swift test)`; run it after every Track A change to `steps.py`/`orientation.py`; record "thresholds frozen on <date> at commit <sha>" in `docs/ios-validation-results.md` once G10's real-data numbers are in.
- Acceptance: `./ios/check.sh` exits 0 on the current `main`; the freeze line exists and names a commit.
- Depends on: IOS-PORT-05, G09, G10. Size S. needs_human: no. Evidence: Inference.

Optional, drafted, not verified — **DEV-01 per-device buffers in server.py**: Sensor Logger's push payload carries `deviceId`/`sessionId` [Verified]; `server.py:12-15` has one global buffer and counter, so two phones streaming to one public URL would mix. Key `buf`/`steps` by `deviceId`, show the active device on the dashboard. Depends on G05. Size M. Only needed if more than one phone will stream to the fallback server during the demo.

---

## 4. Cross-track waves

Track A waves are exactly python-tasks.md §3 (Wave 0 … Wave 12). Track B is placed alongside; nothing in Track B blocks Track A.

| When | Track A (Python; agents) | Track B — mechanism (humans + Mac) | Track B — port (agents, Linux) | Track C — fallback demo |
|---|---|---|---|---|
| **Now** | Wave 0: T01 T04 T05 T06 T19 T20 T40 | **IOS-BG-01** spike app build | **IOS-PORT-01** toolchain | — |
| **Now, humans** | Record the README §2 set (needed by T44/G10; needs no code) | **IOS-BG-02** 10-min pocket runs → decision line: location / audio / Guided Access | — | Install `cloudflared`/`ngrok` on the demo laptop |
| A-Wave 1–2 | T02 T03 T08 T11 T12 T21 → T07 T10a T13 T14 T22 T28 T29 **G09** | IOS-BG-07 Guided Access kiosk + runbook (parallel insurance) | wait for G09 | — |
| A-Wave 3–5 | T09 T23 T28b T29b T31 T32 T39 → T10b T16 T25a T33 T36 G01 → T15 T17 T34 G03 | **IOS-BG-03** keep-alive in the real app → **IOS-BG-04** lifecycle/watchdog | **IOS-PORT-02 → 03 → 04 → 05** (sequential, same package) | — |
| A-Wave 6–9 | T18 T35 **G04** → T24 T37 T41 → T25b T38 T42 G02 → T26 T43 G06 | IOS-BG-05 audio cadence click; IOS-BG-06 CMSensorRecorder + CMPedometer column | **IOS-PORT-06** app shell + field oracle check | **G04** iOS-style simulator |
| A-Wave 10–12 | T27 **T44** G08 → **G05** → G07 **G10** | **IOS-BG-08** end-to-end acceptance run | **IOS-PORT-07** TestFlight | **G05** public URL; cellular test in G10's session |
| After G10 | regenerate oracle | — | **IOS-PORT-08** freeze | — |

Parallelism rules: within a Track A wave everything is parallel (file-sharing pairs already serialised by depends_on, python-tasks.md §3 header). IOS-PORT-02…05 are sequential (one package). IOS-BG tasks are human-gated and run whenever the Mac and a phone are free.

---

## 5. Goal chains (python-tasks.md §5, extended with Track B)

1. **Classify**: T01 → T02 → T07 → T32 → T33 → T34 → T35 → T37 → T38 → G06 → G07; rule guarded by T04 → T28 → T28b (+T11), T39. On device: IOS-PORT-04 reproduces the rule; a trained model on device is **out of scope** for the pitch (the app runs the rule with frozen thresholds; the laptop shows the model).
2. **Count within 3%**: T01 → T08 → (T02, T07) → T09 → T10a → T10b → T15; fixes T28 → T31; live path T12 → T16 → T17 → T18; offline robustness T33 → G02, G01; real data T44 → G10. On device: G09 → IOS-PORT-02…05 → IOS-PORT-06 field check → IOS-BG-08.
3. **A/B/C**: T01 → T02 → T07 → T33 → T34 → T35 → T36; README T40 → T41. (Laptop only.)
4. **Live demo**: primary = IOS-BG-01 → 02 → 03 → 04 → (05, 06) → IOS-PORT-06 → 07 → IOS-BG-08. Fallback = T12 → T31 → T16 → T17 → T18 → T24 → T25b → T26 → T27 → G05 → G07; simulator T20 → T21 → G04; one-command gate G08.

---

## 6. When real recordings arrive (python-tasks.md §6) — unchanged
1. `python3 check_recording.py data/*` (G03) → fix every PROBLEM.
2. `python3 gyro_check.py data/<name>_walk_hand` (T44) → gyro units/sign/rate; if `-gyro` wins, negate in T24.
3. `STEPS_MODEL= python3 evaluate.py --data data` and `--live` (T09/T10b/T15) → 3% gate; decide the still-recording tolerance (risk 8).
4. `thresholds_report.py data`, `ablation.py data` (T39, T36) → retune 0.4 / 2.35 / 5.
5. `python3 train.py` → A/B/C/D tables → README "What this shows" (T41).
6. `./check.sh data` (G08) → paste into README §7 (G10).
7. `python3 oracle_dump.py` (G09) → `./ios/check.sh` (IOS-PORT-08) so the Swift port tracks the final maths.

---

## 7. Risks and open questions (merged)

From python-tasks.md §7 (all still open unless noted): 3 (label flip with model present — use `STEPS_MODEL=`), 7 (T24×T22 gyro guard), 8 (still-recording tolerance), 9 (numpy pin — folded into T37), 10 (matplotlib absent; spectrogram PNG unverified), 11 (unverified on real phones: 100 Hz, gyro sign, arm-swing amplitude vs G_MIN, cloudflared), 12 (identifier assumptions between tasks), 13–14 (T15/T08 numeric assumptions). Risk 5 (no iOS tasks) is **closed by section 3 of this file**, with the caveat that those tasks are not adversarially verified.

From ios-workarounds.md:
- **Biggest**: no source has measured 100 Hz raw `startAccelerometerUpdates` with the screen locked on iOS 16+; the only measurement is CMDeviceMotion at ~10 Hz (99.5% delivery under location keep-alive on iOS 26.5.2). IOS-BG-01/02 exist to measure it on the team's phones before anything else is built.
- Location keep-alive fails silently if the user denies location, if `startUpdatingLocation()` is called after backgrounding, or if the delegate is slow (DTS). IOS-BG-03/04 encode the mitigations.
- Audio keep-alive is a documented App Store rejection when the audio is a pretext; irrelevant for TestFlight internal builds (decisions.md §6) but the audible cadence click (IOS-BG-05) is the legitimate form if that ever changes.
- "Screen locked" vs "input-locked": Guided Access (IOS-BG-07) keeps the app foreground with the screen dark; the slide must say "input-locked" if that is what ships.
- Apple Watch routes (options 12–13) are out: the team owns no watch.
- IOS-PORT-01 depends on the agent container being allowed to download a Swift toolchain (Unverified). If not, the port's acceptance moves to the Mac.

Open decisions for the user:
1. Does the on-board app **replace** the server demo on the day, or run **beside** it (phone streams to the laptop dashboard while also counting locally)? Both are planned; the second needs DEV-01 only if more than one phone streams.
2. Still-recording tolerance for `evaluate.py` once real data exists (python-tasks.md risk 8).
3. Whether to run a verification pass over IOS-PORT-01…08 before assigning them (recommended; ~40 min at this container's 2-agent concurrency).

---

## 8. Dropped during verification (python-tasks.md §8 + ios-workarounds.md §2)
- T10, T25 split (T10a/b, T25a/b); T30 (DC-offset guard) dropped — the failure needs an injected offset no stage produces, and the change measurably hurt slow-walk counts.
- iOS mechanisms refuted: Live Activity as a sampling/display channel; significant-change location; non-mixable audio; haptics in background; honouring lock-screen Pause by deactivating audio; AVSpeechSynthesizer alone; Live Activity + BGAppRefreshTask; CMPedometer/CMMotionActivityManager as the detector; CMBatchedSensorManager; mirrored workout session; CMSensorRecorder as a "near-live" filler.
