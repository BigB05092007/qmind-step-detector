# qmind-step-detector: execution plan

## 1. Objective

Make the phone step detector (README.md:1-16) measurable and honest before the pitch: (1) classify still/walking/running, (2) count steps within 3% of the truth, (3) run the A/B/C orientation experiment so it says what it can actually prove, (4) a live demo that keeps counting when the dashboard is not polling. All of it is built and gated on synthetic data (synth.py) because data/ holds only .gitkeep (Verified); real recordings plug in through the same scripts.

Definition of done:
- Classify: `python3 tests/test_classify.py` exits 0 and `evaluate.py --data data_synth` prints `label accuracy: 100.0%` with the rule after T28 (T10b), the trained model is loadable in `steps.classify` and visible on /state (T38, G07).
- Count: `python3 evaluate.py --data data_synth` ends `overall: true=872 counted=880 err=+0.9%  24/24 recordings within 3%` and exit 0 (T09); the same gate on real recordings is pasted into README section 7 (G10).
- A/B/C: `python3 train.py data_synth` prints per-fold accuracy and confusion tables for A/B/C/D (T34, T35) and README says what B >= C would mean (T41).
- Demo: a 60 s synthetic walk ingested with no GET /state polls counts 108/108 (T12); `./check.sh` prints `CHECK OK` (G08).

## 2. Rules for every agent

- One task per branch, named `task/<id>`; one agent, one sitting.
- Touch only the files listed for the task. Never edit another task's files; if you need a change there, stop and report.
- Do not create new files other than those listed (scratch experiments go under the scratchpad, not the repo).
- Run the task's acceptance command before finishing and paste its output verbatim into the report.
- If the task turns out to be wrong (the problem is not there, the expected number does not reproduce, a dependency landed with different names), stop and report rather than widen the task.
- Label every claim in your report Verified (you read it or ran it), Inference (reasoned, not run) or Unverified (depends on facts outside the container, e.g. a real phone).
- Expected numbers assume numpy 2.4.6 (RNG and QR sign conventions); state your numpy version if a number is off.
- Tasks with needs_human=true are handed to a person; the agent part runs only after the human part is committed.

## 3. Waves

Dependencies fixed relative to the script's input: T26 -> T25b (was T25), T43 -> T10a, T10b (was T10). Added to serialise files edited in parallel: T28 += T08 (steps.py), T31 += T28 (steps.py), T38 += T31 (steps.py, tests/test_steps.py), T16 += T31 (server.py counting site), T34 += T33 (train.py), G02 += T37 (train.py), T15 += T10b (evaluate.py), T29 += T02 (.gitignore), T44 += T43 (README.md), G07 += G05 (server.py, dashboard.html), G10 += G05 (README.md). Waves below are recomputed from the adjusted graph. Within a wave every task can run in parallel unless named otherwise.

### Wave 0 (start now)
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T01 | synth.py: synthetic gait with true steps, true down, gyro | fixtures-eval | synth.py | M | no | - |
| T04 | tests/test_steps.py | frequency | tests/test_steps.py | M | no | - |
| T05 | tests/test_orientation.py | orientation | tests/test_orientation.py | S | no | - |
| T06 | tests/run.py runner | fixtures-eval | tests/run.py | S | no | - |
| T19 | Print a LAN address, not 127.0.0.1 | server-demo | server.py | S | no | - |
| T20 | simulate.py importable: sample() + main guard | server-demo | simulate.py | M | no | - |
| T40 | README: which URL, .true_steps, 127.0.0.1 fallback | docs-repo | README.md | S | no | - |
All parallel (no shared files). Schedule the phone session for T44/G10 now, in parallel with wave 0: the recording needs no code.

### Wave 1
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T02 | make_fixtures.py: 24 synthetic recordings + steps.txt | fixtures-eval | make_fixtures.py, .gitignore | M | no | T01 |
| T03 | eval_dsp.py: cadence, half-rule, down-direction metrics | fixtures-eval | eval_dsp.py | M | no | T01 |
| T08 | steps.count_steps(acc) offline counter | counting | steps.py | S | no | T01 |
| T11 | tests/test_classify.py with known-fail marker | classify-ml | tests/test_classify.py | S | no | T01 |
| T12 | Count inside ingest(); reset_state(); _analyse() | server-demo | server.py | M | no | T01 |
| T21 | Harder simulator: jitter, asym, reorient, offline | server-demo | simulate.py | M | no | T20 |
All parallel.

### Wave 2
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T07 | train.py importable: build_dataset/evaluate, main guard, data_dir | classify-ml | train.py | S | no | T02 |
| T10a | make_fixtures.py --hard | fixtures-eval | make_fixtures.py | S | no | T02 |
| T13 | tests/test_server.py | server-demo | tests/test_server.py | S | no | T01, T12 |
| T14 | tests/test_server_http.py | server-demo | tests/test_server_http.py | M | no | T01, T12 |
| T22 | gravity_complementary: k=0.995 + gyro validation | orientation | orientation.py | S | no | T03 |
| T28 | cadence_hz: 8x zero-pad, ratio 0.6 | frequency | steps.py, tests/test_steps.py | M | no | T03, T04, T08 |
| T29 | spectrogram.py --synth | frequency | spectrogram.py, .gitignore | M | no | T01, T02 |
| G09 | oracle_dump.py: JSON test vectors for the iOS port | fixtures-eval | oracle_dump.py | M | no | T08, T01 |
All parallel.

### Wave 3
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T09 | evaluate.py: counted vs true, 3% gate | fixtures-eval | evaluate.py | M | no | T02, T07, T08 |
| T23 | gravity_lowpass: empty guard, fs param, tau docs + reorient metric | orientation | orientation.py, eval_dsp.py | M | no | T03, T22 |
| T28b | test_classify.py: flip the known-fail | classify-ml | tests/test_classify.py | S | no | T28, T11 |
| T29b | spectrogram.py: recording folder input | frequency | spectrogram.py | S | no | T29, T07, T02 |
| T31 | Min-gap from cadence, not the label | counting | steps.py, server.py | M | no | T08, T12, T28 |
| T32 | Tolerant folder-name parsing | classify-ml | train.py | S | no | T07 |
| T39 | thresholds_report.py | classify-ml | thresholds_report.py | M | no | T07 |
All parallel.

### Wave 4
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T10b | evaluate.py: label accuracy column | fixtures-eval | evaluate.py | S | no | T09, T10a |
| T16 | Ingest exactly one acceleration stream | server-demo | server.py | S | no | T12, T31 |
| T25a | gravity_ok(g) + norm floor | orientation | orientation.py | S | no | T23 |
| T33 | train.load fails clearly, skips folder | classify-ml | train.py | S | no | T32 |
| T36 | ablation.py | classify-ml | ablation.py | M | no | T32 |
| G01 | make_fixtures.py --layout ios | fixtures-eval | make_fixtures.py | S | no | T10a, T09 |
All parallel.

### Wave 5
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T15 | evaluate.py --live | server-demo | evaluate.py | S | no | T09, T12, T10b |
| T17 | Measure sample rate from timestamps | server-demo | server.py | S | no | T16 |
| T34 | train.py: confusion + per-fold accuracy; single-value splits | classify-ml | train.py | M | no | T07, T33 |
| G03 | check_recording.py pre-flight | fixtures-eval | check_recording.py | M | no | T33, T25a, T02 |
All parallel.

### Wave 6
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T18 | Resample buffer to 100 Hz | server-demo | server.py | M | no | T17 |
| T35 | A/B/C/D like-for-like | classify-ml | train.py | S | no | T34 |
| G04 | simulate.py --ios, --seed, --dump, batches | server-demo | simulate.py | M | no | T21, T17 |
All parallel.

### Wave 7
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T24 | server: gyroscope stream + gravity_complementary | server-demo | server.py | M | no | T01, T22, T18 |
| T37 | Save D model to model.joblib | classify-ml | train.py, requirements.txt | M | no | T35 |
| T41 | README: what A/B/C/D proves; synthetic train command | docs-repo | README.md | S | no | T35, T40 |
All parallel.

### Wave 8
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T25b | server refuses to count on implausible gravity; dashboard shows reason | server-demo | server.py, dashboard.html | M | no | T25a, T24 |
| T38 | steps.classify loads model.joblib with rule fallback | classify-ml | steps.py, tests/test_steps.py | M | no | T37, T04, T28, T31 |
| T42 | README: gyro answer + synth/eval_dsp rows | docs-repo | README.md | S | no | T03, T22, T41 |
| G02 | train.load: timestamps, Gravity interpolation, resample | classify-ml | train.py | S | no | T33, T09, T37 |
All parallel.

### Wave 9
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T26 | spm from step intervals | server-demo | server.py, dashboard.html | M | no | T12, T25b |
| T43 | README: Measure accuracy section | docs-repo | README.md, .gitignore | M | no | T10a, T10b, T06, T42 |
| G06 | STEPS_MODEL env var; evaluate.py prints classifier | classify-ml | steps.py, evaluate.py | M | no | T38, T15, T10b |
All parallel.

### Wave 10
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| T27 | Dashboard shows when phone/server went quiet | server-demo | server.py, dashboard.html | M | no | T26 |
| T44 | Real hand-held walk with gyro: units, sign, error | orientation | gyro_check.py, README.md | M | yes | T22, T42, T43 |
| G08 | check.sh one-command gate; git-ignore model.joblib | docs-repo | check.sh, .gitignore | M | no | T43, G03, G06, T10a |
All parallel (T43 and G08 both touch .gitignore but in different waves; G08 appends one line).

### Wave 11
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| G05 | server.py --port / --public-url; README tunnel section | server-demo | server.py, README.md | M | no | T19, T27, T43 |

### Wave 12
| id | title | area | files | size | needs_human | depends_on |
|---|---|---|---|---|---|---|
| G07 | /state and dashboard show which classifier is live | server-demo | server.py, dashboard.html | M | no | G06, T27, G05 |
| G10 | Team records README section 2 set; paste real numbers | docs-repo | README.md | S | yes | G08, T44, G05 |
Parallel (G07 does not touch README).

## 4. Task specifications

### T01 synth.py: importable synthetic gait with true steps, true down vector and gyro
- Problem (Verified): no importable generator. simulate.py:13-26 is an infinite loop POSTing to localhost:8000 (simulate.py:23); train.py:58-59 exits because data/ is empty; gravity_complementary (orientation.py:21-32) has no caller (server.py:7, train.py:17). scratchpad/harness.py:7-30 returns no true down vector and no gyro. scratchpad/dsp/synth2.py is a verified superset (scratchpad/merge/check.py prints `identical ... True True` for three parameter sets).
- Change: create synth.py as a copy of scratchpad/dsp/synth2.py minus the `sys.path.insert` line and with `FS = 100` replaced by `from orientation import FS`. API: `make(mode_seq, seed=0, stride_asym=0.0, swing_deg=0.0, f_walk=1.8, f_run=2.8, amp_walk=3.0, amp_run=9.0, width=0.06, noise=0.25) -> (acc (N,3) m/s^2 phone frame, true_steps int, true_down (N,3) unit, gyro (N,3) rad/s body frame)` and `ang_err_deg(est, true) -> (N,) deg`. mode_seq = list of (mode, seconds), mode in {still, walk, run}. Heel-strike formula identical to simulate.py:18-19. Gyro sign satisfies orientation.py:29-30 (`rotated = g[i-1] - cross(gyro[i]*dt, g[i-1])`): with M_i the phone-frame rotation, dM = M_i @ M_{i-1}.T, theta = [dM[2,1]-dM[1,2], dM[0,2]-dM[2,0], dM[1,0]-dM[0,1]]/2, gyro[i] = -theta*FS, gyro[0] = 0. 3-line docstring stating the return tuple.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth; from orientation import gravity_complementary, FS; a,n,d,g=synth.make([('walk',30)],swing_deg=30); print(a.shape,n); print(round(float(synth.ang_err_deg(gravity_complementary(a,g,k=1.0),d)[2*FS:].mean()),2))"` prints exactly `(3000, 3) 54` then `0.67`. `python3 -c "import synth; a,n,d,g=synth.make([('walk',10)]); print(a.shape,n,d.shape,g.shape)"` prints `(1000, 3) 18 (1000, 3) (1000, 3)`. `python3 -c "import synth; print(synth.make([('run',60)], f_run=3.2, amp_run=9.0)[1], synth.make([('walk',60)], f_walk=1.4, amp_walk=2.0)[1])"` prints `192 83`. `grep -c 'sys.path' synth.py` prints `0`.
- Depends on: none. Size M.
- Notes: verifier re-ran all three commands on scratchpad/verify-fixtures-eval/synth.py. Determinism relies on numpy 2.4.6 RNG/QR conventions (Inference); every expected number downstream inherits this.

### T02 make_fixtures.py: 24 deterministic synthetic recordings in train.py's folder layout with steps.txt
- Problem (Verified): data/ has only .gitkeep; train.py:54 globs `data/*`, train.py:55 splits the basename into person/activity/placement, train.py:33 reads x,y,z by name. README.md:51 asks for steps.txt but nothing writes or reads it. Verifier regenerated 24 folders and ran unmodified train.py: `976 windows from 4 people, placements: ['hand', 'pocket']`, A 89% / B 100% / C 94%.
- Change: make_fixtures.py importing `make` from synth and `FS` from orientation. `write_recording(folder, acc, true_steps)`: makedirs(exist_ok); `t = np.arange(len(acc))/FS`; write TotalAcceleration.csv (pandas, index=False) with columns exactly `time,seconds_elapsed,x,y,z`, `time = (t*1e9).astype(np.int64)`, `seconds_elapsed = t`; write steps.txt = `f"{true_steps}\n"`. Never delete or empty the target directory. Main: argparse `--out DIR` (default data_synth), `--seed INT` (default 0); `seed = args.seed`; `for person in ['p1','p2','p3','p4']: for activity, secs in [('walk',30),('run',20),('still',20)]: for placement, kw in [('hand',{'swing_deg':30}),('pocket',{'stride_asym':0.5})]: seed += 1; acc, true, *_ = make([(activity,secs)], seed=seed, **kw); write_recording(f'{args.out}/{person}_{activity}_{placement}', acc, true)`. Append `data_synth*/` to .gitignore. Under 45 lines.
- Acceptance: `cd /home/user/qmind-step-detector && rm -rf data_synth && python3 make_fixtures.py --out data_synth && ls data_synth | wc -l && head -1 data_synth/p1_walk_hand/TotalAcceleration.csv && wc -l < data_synth/p1_walk_hand/TotalAcceleration.csv && cat data_synth/p1_walk_hand/steps.txt data_synth/p1_run_hand/steps.txt data_synth/p1_still_hand/steps.txt && grep -c 'data_synth' .gitignore` prints `24`, `time,seconds_elapsed,x,y,z`, `3001`, `54`, `55`, `0`, `1`. Then `mkdir -p /tmp/tcwd && ln -sfn /home/user/qmind-step-detector/data_synth /tmp/tcwd/data && cd /tmp/tcwd && python3 /home/user/qmind-step-detector/train.py | head -1` prints `976 windows from 4 people, placements: ['hand', 'pocket']` (valid until T07 changes train.py's CLI; after T07 use its data_dir argument instead).
- Depends on: T01. Size M.
- Notes: column names from scratchpad/sl/README.md:114,118 and sl/UNITS.md:9-10 (Verified docs). A tree written with --hard (T10a) has 26 folders; T07's 976-window figure needs a plain run.

### T03 eval_dsp.py: cadence, half-rule and down-direction metrics on synthetic data
- Problem (Verified): nothing in the repo measures cadence error, half-rule failures (steps.py:21-23) or orientation error; harness.py:55-56 prints only counts and cadence sets. The defects T22/T23/T25/T28 fix were established with scratch scripts not in the repo.
- Change: eval_dsp.py (no args, exit 0) using synth.make seed 0. vertical = `vertical_horizontal(acc, gravity_lowpass(acc))[0]`; windows = `[v[s:s+200] for s in range(100, len(v)-200, 50)]`. Six lines, values `round(float(x), 3)`: (1) `cadence worst_median_abs_err_hz=<x>` = max over f_true in `np.arange(1.5, 3.31, 0.1)` (mode walk if f_true<2.4 else run; `make([(mode,30)], f_walk=f_true, f_run=f_true)`) of `np.median(|cadence_hz(w)-f_true|)`; (2) `halving run2.8_asym1.0=<frac> walk1.8_asym1.0=<frac>` = fraction of windows with cadence < 0.75*f_true for `make([('run',30)], stride_asym=1.0)` and `make([('walk',30)], stride_asym=1.0)`; (3) `doubling walk1.8_width0.02=<frac>` = fraction > 1.5*1.8 for `make([('walk',30)], width=0.02)`; (4) `down_err_deg lowpass walk=<x> run=<x> walk_swing30=<x> run_swing30=<x>` = `synth.ang_err_deg(gravity_lowpass(acc), true_down)[200:].mean()` for `make([(m,30)])` and `make([(m,30)], swing_deg=30)`; (5) same with prefix `down_err_deg complementary` using `gravity_complementary(acc, gyro)` defaults; (6) `reorient settle_s tau1.0=<x>`: a1 seed 0 walk 15 s, a2 seed 7 walk 15 s, vstack acc and down, `e = synth.ang_err_deg(gravity_lowpass(acc, tau_s=1.0), down)`, value = `np.argmax(e[1500:] < 5) / FS`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 eval_dsp.py; echo exit=$?` on the unmodified steps.py/orientation.py prints exactly these six lines then `exit=0`: `cadence worst_median_abs_err_hz=0.5`, `halving run2.8_asym1.0=0.759 walk1.8_asym1.0=0.259`, `doubling walk1.8_width0.02=0.0`, `down_err_deg lowpass walk=0.433 run=0.311 walk_swing30=18.603 run_swing30=18.727`, `down_err_deg complementary walk=0.827 run=0.593 walk_swing30=0.819 run_swing30=0.578`, `reorient settle_s tau1.0=2.51`. Runs in about 2 s.
- Depends on: T01. Size M.
- Notes: verifier's literal implementation (scratchpad/verify-fixtures-eval/eval_dsp.py, 50 lines) printed exactly these lines in 1.9 s.

### T04 tests/test_steps.py: regression tests for cadence_hz, classify, detect_steps
- Problem (Verified): steps.py has no tests; cadence_hz half-rule (steps.py:21-23), state-dependent min_gap (steps.py:56), classify thresholds (steps.py:44-46) can be broken silently. pytest is not installed.
- Change: tests/test_steps.py, plain asserts. `sys.path.insert(0, dirname(dirname(abspath(__file__))))`; import FS, cadence_hz, classify, detect_steps. Helpers `sine(f, secs)` = sin(2 pi f t) and `spikes(f, secs, amp=3.0)` = amp*exp(-((ph-0.1)/0.06)**2) - amp*0.15, ph=(f*t)%1, t=np.arange(secs*FS)/FS. test_cadence_resolution: |cadence_hz(sine(1.8,10))-1.8|<1e-6, |cadence_hz(sine(2.8,10))-2.8|<1e-6; cadence_hz(sine(1.8,2))==2.0 and cadence_hz(sine(2.8,2))==3.0 with comment 'documents the 0.5 Hz bins of a raw 2 s window; T28 relaxes this'. test_cadence_harmonic: cadence_hz(sine(1.8,10)+0.8*sine(3.6,10))≈1.8; cadence_hz(spikes(1.8,10))≈1.8; cadence_hz(spikes(2.8,10))≈2.8 (abs 1e-6). test_classify: {'v_std':0.1,'cadence_hz':2.0}->STILL; {'v_std':2.0,'cadence_hz':1.8}->WALKING; {'v_std':2.0,'cadence_hz':3.0}->RUNNING; {'v_std':6.0,'cadence_hz':1.5}->RUNNING. test_detect_steps: len(detect_steps(spikes(1.8,10),'WALKING'))==18; (spikes(2.8,10),'RUNNING')==28; (spikes(2.8,10),'STILL')==0; (spikes(2.8,10),'WALKING')==14 with comment 'known limitation: wrong state halves a running count (T31)'. `__main__`: run all test_* and print('ok'). No import of synth.py.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_steps.py; echo exit=$?` -> prints `ok` then `exit=0`. Negative check: `python3 -c "import sys; sys.path.insert(0,'.'); import tests.test_steps as t; t.test_detect_steps()"` exits 0; editing steps.py:56 to 0.4 for RUNNING would make it raise AssertionError (28 becomes 14).
- Depends on: none. Size M.
- Notes: all 18 values re-derived (scratchpad/verify-frequency/t04_check.py); the literal file is 52 lines.

### T05 tests/test_orientation.py: regression tests for gravity_lowpass, gravity_complementary, vertical_horizontal
- Problem (Verified): orientation.py has no tests; gravity_complementary (orientation.py:21-32) has no caller; T22/T23/T25a all edit orientation.py.
- Change: tests/test_orientation.py, plain asserts; sys.path insert of the repo root; import FS, gravity_lowpass, gravity_complementary, vertical_horizontal, cadence_hz. Fixture `rng = np.random.default_rng(1); R, _ = np.linalg.qr(rng.normal(size=(3, 3)))`; phone-frame acc = `world @ R`. test_static_down: world = tile([0,0,9.81],(500,1)); g = gravity_lowpass(acc); v,h,down = vertical_horizontal(acc,g); assert max|down[-1] - R.T@[0,0,1]| < 1e-6, |v[-1]| < 1e-6, h[-1] < 1e-6. test_complementary_zero_gyro: same with gravity_complementary(acc, zeros_like(acc)). test_bounce_cadence_after_rotation: z = 9.81 + 2 sin(2 pi 1.8 t) for 10 s, acc = world @ R; assert |cadence_hz(v[FS:]) - 1.8| < 0.15 and h[FS:].max() < 1e-6. `__main__` runs the three and prints ok.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_orientation.py; echo exit=$?` -> prints `ok` then `exit=0`. Negative check: `python3 -c "import sys; sys.path.insert(0,'tests'); import test_orientation as t; t.R[:] = 0; t.test_static_down()"` must exit non-zero.
- Depends on: none. Size S.
- Notes: measured static error 6.7e-16, cadence 1.7778 Hz; still passes after T22/T23/T25a (scratchpad/verify-orientation/t05_tests.py).

### T06 tests/run.py: dependency-free test runner
- Problem (Verified): pytest not installed; no tests/ dir; a plain `python3 tests/run.py` puts tests/ first on sys.path so `import steps` fails without the runner adding the root.
- Change: tests/run.py (~25 lines): `HERE = dirname(abspath(__file__))`; `sys.path.insert(0, dirname(HERE))` before importing tests. Optional substring filter `sys.argv[1]` on the basename. For each sorted `test_*.py`: load via importlib.util.spec_from_file_location + exec_module; for each sorted callable `test_*` attribute call inside try/except Exception: print `PASS {name}` or `FAIL {name}: {exc!r}` (stdout) plus traceback to stderr. Finally print `{passed} passed, {failed} failed`, `sys.exit(1 if failed else 0)`. Do not reset server globals here.
- Acceptance: `cd /home/user/qmind-step-detector && mkdir -p tests && printf 'import steps\ndef test_ok():\n    assert steps.classify({"v_std": 0.1, "cadence_hz": 0}) == "STILL"\ndef test_fail():\n    assert False\n' > tests/test_zz_tmp.py && python3 tests/run.py zz_tmp 2>/dev/null; echo exit=$?; rm tests/test_zz_tmp.py; python3 tests/run.py 2>/dev/null | tail -1; echo exit=$?` prints `FAIL test_fail: AssertionError()`, `PASS test_ok`, `1 passed, 1 failed`, `exit=1`, then a line ending `, 0 failed` and `exit=0`.
- Depends on: none. Size S.
- Notes: prototyped in scratchpad/verify-fixtures-eval/tests/run.py. T11's known-fail case must not be named test_*.

### T07 Make train.py importable: build_dataset/evaluate, main guard, data_dir argument
- Problem (Verified): train.py:53-74 runs at import; train.py:58-59 `sys.exit` kills importers (`python3 -c 'import train'` exits 1); train.py:54 globs the relative `data/*`.
- Change: move lines 53-61 into `def build_dataset(data_dir)` globbing `os.path.join(data_dir, '*')`, same row dicts, `raise SystemExit(f'No recordings in {data_dir} yet.')` when empty, print the summary line, return df. Move lines 63-74 into `def evaluate(df)`. Bottom: `if __name__ == '__main__': data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'); evaluate(build_dataset(data_dir))`. Keep load(), windows(), WIN and output unchanged. Run `python3 make_fixtures.py --out data_synth` first for the acceptance.
- Acceptance: `cd /tmp && python3 -c "import sys; sys.path.insert(0,'/home/user/qmind-step-detector'); import train; print('imported', callable(train.build_dataset), callable(train.evaluate), train.load.__name__)"` prints exactly `imported True True load` within 5 s and no accuracy lines. `cd /home/user/qmind-step-detector && python3 train.py data_synth; echo exit=$?` prints `976 windows from 4 people, placements: ['hand', 'pocket']`, then the two Leave-one-*-out blocks with the placement block reading `A 89%`, `B 100%`, `C 94%` and the person block all 100%, then `exit=0`. `mkdir -p /tmp/empty_data && python3 train.py /tmp/empty_data; echo exit=$?` prints `No recordings in /tmp/empty_data yet.` and `exit=1`.
- Depends on: T02. Size S.
- Notes: per-fold A hand 78% pocket 100%; C hand 100% pocket 88% (scratchpad/verify-classify-ml/exp_train.py).

### T08 steps.count_steps(acc): one-pass offline counter mirroring server.state()
- Problem (Verified): counting exists only inside server.state() (server.py:47-50) on GET /state polls. A naive one-pass count gives 100/128 on a mixed recording (WALKING min_gap 0.4 s, steps.py:56); a 0.2 s-hop windowed replay reproduces the live count on all 24 fixtures (880 vs 872 true). Empty input raises IndexError in gravity_lowpass (orientation.py:15).
- Change: in steps.py add `from orientation import gravity_lowpass, vertical_horizontal` next to `from orientation import FS` and, after detect_steps:
```
def count_steps(acc, hop_s=0.2):
    """Offline twin of server.state() (after T12: server._count_locked()); keep the two in sync."""
    acc = np.asarray(acc, float)
    if len(acc) < 3 * FS:
        return 0, []
    if np.median(np.linalg.norm(acc, axis=1)) < 3:   # g units, mirror server.py:39-40
        acc = acc * 9.81
    g = gravity_lowpass(acc)
    v, h, _ = vertical_horizontal(acc, g)
    hop = int(hop_s * FS)
    count, last, states = 0, -10 ** 9, []
    for end in range(3 * FS, len(v) + 1, hop):
        w = slice(end - 2 * FS, end)
        feat = features(v[w], h[w])          # T31 reads feat['cadence_hz'] here
        st = classify(feat)
        states.append(st)
        lo = max(0, end - 4 * FS)
        for p in detect_steps(v[lo:end], st):
            gi = lo + p
            if gi > last + 0.25 * FS and gi < end - 0.2 * FS:
                count += 1; last = gi
    return count, states
```
No other files.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import numpy as np, synth; from steps import count_steps; a,t,*_=synth.make([('walk',20),('run',20),('walk',20)],seed=99); print(count_steps(a)[0], t); a,t,*_=synth.make([('run',60)],seed=3,stride_asym=1.0); print(count_steps(a)[0], t); print(count_steps(np.zeros((0,3))), count_steps(a/9.81)[0])"` prints exactly `128 128`, then `168 167`, then `(0, []) 168`.
- Depends on: T01. Size S.
- Notes: numbers identical under base, T28, T31 and T28+T31 (scratchpad/verify-counting/t08_check.py). Hop 0.5 s drops the asym run to 133; keep 0.2.

### T09 evaluate.py: counted vs true steps per recording and overall, 3% gate
- Problem (Verified): README.md:92 sets 'within 3%', README.md:51 asks for steps.txt, nothing reads it. `import train` exits 1 until T07.
- Change: evaluate.py (~45 lines), argparse `--data DIR` (default data). `from train import load`, `from steps import count_steps`. For each sorted directory in DIR: no steps.txt -> print `warning: {name}: no steps.txt, skipped`; else acc = load(folder), true = int(steps.txt), `count, states = count_steps(acc)`, `err_pct = (count-true)/true*100 if true else nan`, `ok = abs(err_pct) <= 3.0 if true else count == 0`. Row: `f"{name:24s} true={true:4d} counted={count:4d} err={err_pct:+6.1f}% {'ok' if ok else 'FAIL'}"`, with the literal `err=   n/a ` when true==0. No rows -> print `no recordings found`, exit 2. Else `overall_err = (C-T)/T*100 if T else 0.0`, print `f"overall: true={T} counted={C} err={overall_err:+.1f}%  {n_ok}/{n} recordings within 3%"`, `sys.exit(0 if abs(overall_err) <= 3 and n_ok == n else 1)`.
- Acceptance: `cd /home/user/qmind-step-detector && rm -rf data_synth && python3 make_fixtures.py --out data_synth && python3 evaluate.py --data data_synth; echo exit=$?` prints 24 rows including `p1_run_hand              true=  55 counted=  56 err=  +1.8% ok`, `p1_still_hand            true=   0 counted=   0 err=   n/a  ok`, every walk row `true=  54 counted=  54 err=  +0.0% ok`, then `overall: true=872 counted=880 err=+0.9%  24/24 recordings within 3%` and `exit=0`. Also `python3 evaluate.py --data data; echo exit=$?` prints `no recordings found` and `exit=2`.
- Depends on: T02, T07, T08. Size M.
- Notes: numbers hold only if T08 is implemented exactly as specified (hop 20, warm-up 300, 4 s detection window).

### T10a make_fixtures.py --hard
- Problem (Verified): default fixtures all pass; a stride_asym 1.0 run is labelled WALKING in 201/286 hops (steps.py:21-23 half rule) though the count survives; no mixed recording exists; a mixed folder in the training tree would be parsed as activity 'mixed' (train.py:55).
- Change: add `--hard` (store_true). When set, after the 24 folders write `write_recording(f'{args.out}/dave_run_pocket', *make([('run',60)], seed=3, stride_asym=1.0)[:2])`, `write_recording(f'{args.out}/dave_walk_pocket', *make([('walk',60)], seed=7, stride_asym=1.0)[:2])`, and `erin_mixed_pocket` = `make([('walk',20),('run',20),('walk',20)], seed=99)` ONLY under `f'{args.out}_mixed'`. ~8 lines.
- Acceptance: `cd /home/user/qmind-step-detector && rm -rf data_synth data_synth_mixed && python3 make_fixtures.py --out data_synth --hard && ls data_synth | wc -l && ls data_synth_mixed && cat data_synth/dave_run_pocket/steps.txt data_synth/dave_walk_pocket/steps.txt data_synth_mixed/erin_mixed_pocket/steps.txt` prints `26`, `erin_mixed_pocket`, `167`, `108`, `128`.
- Depends on: T02. Size S.
- Notes: verified with scratchpad/verify-fixtures-eval/make_fixtures.py --hard.

### T10b evaluate.py: per-recording label accuracy column and overall label accuracy
- Problem (Verified): on dave_run_pocket the count passes (168/167) while 201 of 286 hop states are WALKING; evaluate.py prints nothing about `states`.
- Change: expected label from `{'walk':'WALKING','run':'RUNNING','still':'STILL'}.get(name.split('_')[1])`; None -> print `label= n/a` and exclude from the overall figure; else `pct = 100*sum(s == expected for s in states)/len(states)`, append ` label={pct:3.0f}%` to the row. Accumulate matching/total hops; after the overall line print `label accuracy: {100*matching/total:.1f}%`. Exit code unchanged. ~12 lines.
- Acceptance: `cd /home/user/qmind-step-detector && rm -rf data_synth data_synth_mixed && python3 make_fixtures.py --out data_synth --hard && python3 evaluate.py --data data_synth | grep -E 'dave|overall|label accuracy'; echo exit=$?` prints `dave_run_pocket          true= 167 counted= 168 err=  +0.6% ok label= 30%` (on the unmodified steps.cadence_hz; `label=100%` once T28 has merged), `dave_walk_pocket         true= 108 counted= 108 err=  +0.0% ok label=100%`, `overall: true=1147 counted=1156 err=+0.8%  26/26 recordings within 3%`, `label accuracy: 93.4%` (100.0% once T28 has merged) and `exit=0`. `python3 evaluate.py --data data_synth_mixed | grep erin` prints `erin_mixed_pocket        true= 128 counted= 128 err=  +0.0% ok label= n/a`.
- Depends on: T09, T10a. Size S.
- Notes: the 30%/93.4% figures also flip to 100% whenever model.joblib is present (critic, measured in scratchpad/gaps/e4_model_present.py): run this acceptance with no model.joblib in the repo root, or with `STEPS_MODEL=` once G06 has landed.

### T11 tests/test_classify.py: synthetic regression test for the rule, known half-cadence failure marked
- Problem (Verified): no test of steps.classify (steps.py:42-46); the stride_asym 1.0 run failure (cadence halved to 1.5 Hz, v_std 3.67 < 5) is recorded nowhere. Seed 7 gives 17/54 RUNNING. A model-backed classify (T38) would silently change the result, so the test must pin the rule.
- Change: tests/test_classify.py with the repo root on sys.path; `from synth import make`, `from orientation import FS, gravity_lowpass, vertical_horizontal`, `from steps import features`, and `try: from steps import classify_rule as classify / except ImportError: from steps import classify`. Helper `frac(mode, label, **kw)`: `acc = make([(mode, 30)], seed=7, **kw)[0]; v, h, _ = vertical_horizontal(acc, gravity_lowpass(acc)); labels = [classify(features(v[s:s+2*FS], h[s:s+2*FS])) for s in range(FS, len(acc)-2*FS, FS//2)]; return labels.count(label)/len(labels)`. test_still: frac('still','STILL')==1.0; test_walk: frac('walk','WALKING')>=0.95; test_walk_swing: frac('walk','WALKING',swing_deg=30)>=0.95; test_run: frac('run','RUNNING')>=0.95. Not a test_: `known_fail_run_asym()` prints `KNOWN-FAIL run stride_asym=1.0 {f:.2f}` if f<0.9 else `PASS run stride_asym=1.0 {f:.2f} -- rename to test_run_asym`. `__main__`: run the four tests printing `PASS <name>` (or `FAIL <name>` and exit 1), then known_fail_run_asym(), exit 0.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_classify.py; echo exit=$?` prints `PASS test_still`, `PASS test_walk`, `PASS test_walk_swing`, `PASS test_run`, then `KNOWN-FAIL run stride_asym=1.0 0.31` (17 of 54 windows with seed 7) and `exit=0`. After T28 the same command is expected to print `PASS run stride_asym=1.0 ...`; then rename the function to test_run_asym.
- Depends on: T01. Size S.
- Notes: fractions re-measured for seeds 7 and 3 (scratchpad/verify-classify-ml/exp_thresholds.py).

### T12 Count steps inside ingest(); add reset_state() and _analyse()
- Problem (Verified): steps['count'] increments only in state() (server.py:47-50), which runs only on GET /state (server.py:67-69; dashboard polls at 200 ms, dashboard.html:47). 60 s walk with no polling -> 7/108; polled every 5 s -> 84; every 0.2 s -> 108 (scratchpad/verify-server-demo/baseline.py). Globals at server.py:12-15 have no reset.
- Change: (1) `def _analyse(b)`: None when len(b) < 3*FS, else `(idx, acc, vert, horiz, down, feat, st)` using exactly lines 38-45. (2) `def _count_locked()` (lock held): `b = np.array(buf)`; r = _analyse(b); return if None; then the detect_steps loop of lines 47-50 unchanged. (3) `last_counted = [0]`; in ingest() right after `buf.append(...)` (server.py:30): `if n_seen[0] - last_counted[0] >= FS // 5: last_counted[0] = n_seen[0]; _count_locked()`. (4) state() read-only: copy b under lock, _analyse, return {'ready': False} or the same JSON as today without touching `steps`. (5) `def reset_state()`: under lock buf.clear(); n_seen[0] = 0; grav[0] = None; last_counted[0] = 0; steps.update(count=0, last=-10**9). /reset handler stays count-only.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth, server; a,t,*_=synth.make([('walk',60)]); server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a]); print(t, server.steps['count']); server.reset_state(); print(server.steps['count'], len(server.buf))"` prints `108 108` (before the change `108 0`) then `0 0`. Also `python3 -c "import synth, server; a,t,*_=synth.make([('walk',60)])\nfor i in range(0,len(a),500):\n    server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a[i:i+500]]); server.state()\nprint(t, server.steps['count'])"` prints `108 108` (5 s packets; currently prints `108 84`).
- Depends on: T01. Size M.
- Notes: reproduced on scratchpad/verify-server-demo/patched/server.py. `lock` is a plain Lock; _count_locked() must never re-acquire it.

### T13 tests/test_server.py: in-process smoke test
- Problem (Verified): server's live path (ingest server.py:19-30, state :33-56, iOS merge :27-28, g rescale :39-40) is only exercised via HTTP and the dashboard.
- Change: tests/test_server.py, plain asserts, repo root on sys.path, `server.reset_state()` at the start of every test. Helper `replay(acc, stream='totalacceleration', poll=20)`: ingest 20-sample packets, state() after each, collect `s['state']` when ready, return (server.steps['count'], states). test_not_ready_before_3s: `synth.make([('walk', 5)])[0][:250]`, every state() has `ready` False (check only `ready`). test_walk_count: seed 5 walk 30 s; |n-true|/true <= 0.03 and set(st) == {'WALKING'}. test_ios_streams: g=[0,0,9.81]; per sample send gravity then accelerometer (acc-g) packets of 20; count == 54. test_state_keys: last state has at least {'ready','state','steps','cadence','spm','down','tilt','freqs','amp','vertical'}. `__main__` runs sorted test_* and prints ok.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_server.py; echo exit=$?` prints `ok` and `exit=0`.
- Depends on: T01, T12. Size S.
- Notes: 54/54 via both paths, 136 ready windows WALKING, first 13 state() calls not ready (baseline.py, accept.py).

### T14 tests/test_server_http.py: HTTP smoke test on a free port
- Problem (Verified): handler server.py:59-81 is only run on port 8000; bad JSON swallowed with a print (server.py:77-80); /reset count-only (server.py:76); GET / serves dashboard.html (server.py:71). Untested.
- Change: start `ThreadingHTTPServer(('127.0.0.1', 0), server.H)` in a daemon thread; helpers get(path)->JSON, post(path, bytes)->status. server.reset_state() first. (1) get('/state')['ready'] False. (2) seed 5 walk 30 s posted as 20-sample `{'payload': [...]}` packets with get('/state') after each; final: ready True, state WALKING, |steps-true|/true <= 0.03. (3) post('/reset', b'') 200 and get('/state')['steps'] == 0. (4) GET / body starts with `b'<!doctype html>'`. (5) post('/data', b'not json') 200 and get('/state')['ready'] True. srv.shutdown(). Same `__main__` as T13.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_server_http.py; echo exit=$?` prints one `bad packet: Expecting value: line 1 column 1 (char 0)` line from the in-process server, then `ok`, and `exit=0`.
- Depends on: T01, T12. Size M.
- Notes: scratchpad/verify-server-demo/http_smoke.py ran this sequence on the unmodified server.

### T15 evaluate.py --live
- Problem (Verified): pre-T12 the live count depends on poll rate (p1_walk_hand: 42/54 at 5 s, 54/54 at 0.2 s); evaluate.py measures only count_steps.
- Change: add `--live` (store_true) and `--poll-s` (float, default 0.2). When set, per recording: import server; server.reset_state(); for i in range(0, len(acc), int(poll_s*FS)): ingest totalacceleration packets; server.state(); live = server.steps['count']. Column `live={live:4d}` per row and a `live overall: true=<T> counted=<C> err=<pct>` line. ~20 lines. Exit code stays offline-based.
- Acceptance: `cd /home/user/qmind-step-detector && python3 evaluate.py --data data_synth --live | tail -2` shows a `live overall: true=872 counted=<C>` line with C within 3% of 872 (846..898; expected 880), and `python3 evaluate.py --data data_synth --live --poll-s 5 | grep p1_walk_hand` shows `counted=  54` and `live=  54` (with T12 merged; on the pre-T12 server this reads live=  42).
- Depends on: T09, T12, T10b. Size S.
- Notes: equality of live and offline counts is an Inference from T08's design; gated on the 3% band. After T10b the `label=` column precedes `live=` or follows it; keep the T09 label column intact.

### T16 Ingest exactly one acceleration stream
- Problem (Verified): ingest appends for both `totalacceleration` and `accelerometer` (server.py:26-30); both streams -> n_seen 12000 for 60 s, cadence 1.0 Hz (spm 60). Android-only trigger (sl/UNITS.md:18-19).
- Change: `src = [None]`. At the top of the `elif name in ('totalacceleration', 'accelerometer')` branch: `if src[0] is None or (name == 'totalacceleration' and src[0] == 'accelerometer'): src[0] = name; buf.clear()` (T17 adds tbuf.clear() here); then `if name != src[0]: continue`. Do NOT reset n_seen, last_counted or steps['last']. Add `src[0] = None` to reset_state() only.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth, server; a,t,*_=synth.make([('walk',60)])\nfor i in range(0,len(a),20):\n    pl=[]\n    for v in a[i:i+20]: pl += [{'name':'accelerometer','values':dict(zip('xyz',v))},{'name':'totalacceleration','values':dict(zip('xyz',v))}]\n    server.ingest(pl); s=server.state()\nprint(server.n_seen[0], s['cadence'], server.steps['count'])"` prints `6001 2.0 108` (currently `12000 1.0 108`; after T28 the cadence prints about 1.81).
- Depends on: T12, T31. Size S.
- Notes: resetting n_seen on switch would make the dedup at server.py:49 reject steps for ~30 s (Inference, traced).

### T17 Measure the real sample rate from packet timestamps
- Problem (Verified): ingest ignores `time` (server.py:21-30); everything assumes FS=100. 50 Hz feed -> RUNNING 271/271, 82/108 steps. Sensor Logger `time` is epoch ns (sl/PUSHING.md:38, sl/UNITS.md:9).
- Change: `tbuf = collections.deque(maxlen=8 * FS)`; per accepted sample append `None if t is None else t / 1e9` (ns only). `def measured_fs()`: ts = non-None; None if len < 2*FS else `(len(ts) - 1) / (ts[-1] - ts[0])`. state() adds `fs_measured` to both dicts; if not None and |fs-FS|/FS > 0.1 print once (`_warned = [False]`) `WARNING: phone sends {fs:.0f} Hz, server assumes {FS} Hz -- set Sensor Logger to 100 Hz`. Clear tbuf in reset_state() and in T16's buf.clear().
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import server; server.ingest([{'name':'totalacceleration','time':i*20_000_000,'values':{'x':0,'y':0,'z':9.81}} for i in range(400)]); print(round(server.measured_fs(),1)); server.reset_state(); server.ingest([{'name':'totalacceleration','values':{'x':0,'y':0,'z':9.81}} for i in range(400)]); print(server.measured_fs())"` prints `50.0` then `None`. Real epoch-ns input (1698501144401773000 + i*10_000_000 for 400 samples) gives 100.0.
- Depends on: T16. Size S.
- Notes: ns/ms/s heuristic was refuted; parse ns only.

### T18 Resample the buffer to 100 Hz when the measured rate differs
- Problem (Verified): _analyse still treats the buffer as 100 Hz; 50 Hz walk -> 82/108. The dedup at server.py:49 is in sample-index units; interpolating the raw sample-number column leaves 50 Hz units and drops a 50 Hz run to 84/167 (scratchpad/verify-server-demo/t18_variant.py).
- Change: `t0 = [None]` set on the first non-None time, reset in reset_state(). `def _resampled(b, ts) -> (idx, acc)`: raw `(b[:, 0].astype(int), b[:, 1:])` when empty, any t None, fs None, |fs-FS|/FS <= 0.05 or `np.any(np.diff(t) <= 0)`; else `grid = np.arange(t[0], t[-1], 1/FS)`, acc = np.interp per column, `idx = np.round((grid - t0[0]) * FS).astype(int)`. In _analyse replace the idx/acc line with `_resampled(b, ts)` and do the `len(acc) < 3*FS` check after resampling; `ts = list(tbuf)` copied under the same lock as b and passed in from _count_locked() and state().
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth, server; from collections import Counter; st=[]\nfor mode in ('walk','run'):\n    server.reset_state(); a,t,*_=synth.make([(mode,60)]); a=a[::2]; st=[]\n    for i in range(0,len(a),10):\n        server.ingest([{'name':'totalacceleration','time':int((i+j)*20_000_000),'values':dict(zip('xyz',v))} for j,v in enumerate(a[i:i+10])]); s=server.state(); st.append(s.get('state'))\n    print(mode, t, server.steps['count'], Counter(st).most_common(1)[0][0])"` prints `walk 108 <n> WALKING` with n in 105..111 and `run 167 <m> RUNNING` with m in 162..172, preceded by one WARNING line from T17 (currently `walk 108 82 RUNNING`).
- Depends on: T17. Size M.
- Notes: patched copy gives walk 108, run 168; 100 Hz with timestamps still 108/108.

### T19 Print a LAN address the phone can reach
- Problem (Verified): server.py:85 gethostbyname(gethostname()) returns 127.0.0.1 here; the UDP-connect trick returns 192.0.2.2.
- Change: `def local_ip()`: UDP socket, `connect(('10.255.255.255', 1))`, return `getsockname()[0]`; fallback to gethostbyname on any exception; close in finally. In `__main__` use it; if it starts with `127.` also print `Could not find your hotspot IP -- run ifconfig / ipconfig and use the 192.168.x.x or 172.20.x.x address instead.`
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import server; ip=server.local_ip(); print(ip); assert not ip.startswith('127.'), ip"` prints a non-loopback address (here `192.0.2.2`) and exits 0; `python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))"` prints `127.0.0.1` for comparison.
- Depends on: none. Size S.
- Notes: touches only the `__main__` block.

### T20 Make simulate.py importable: sample() plus main guard
- Problem (Verified): module-level infinite loop (simulate.py:13-26); `import simulate` exits 1 with URLError; toggle thread (simulate.py:8-11) raises EOFError without a tty; docstring (simulate.py:2) claims it prints the count but it writes `.true_steps` (simulate.py:25).
- Change: `def sample(mode, phase, rng, asym=0.0, jitter=0.0)` advancing one 1/FS tick, returning `(world, phase, stepped)` with world from simulate.py:17-20 (noise `rng.normal(0, 0.25, 3)`), stepped True when int(phase) increased; asym/jitter accepted but unused. Toggle thread, R (from rng), HTTP loop and `.true_steps` write go into `def main(url='http://localhost:8000/data')` under `if __name__ == '__main__': main()`. Also print `true steps: {true_steps}` to stderr each second. `rng = np.random.default_rng()`.
- Acceptance: `cd /home/user/qmind-step-detector && timeout 10 python3 -c "import numpy as np, simulate; rng=np.random.default_rng(0); w,ph,st=simulate.sample('walk',0.0,rng); print(w.shape, round(ph,3), st); w,ph,st=simulate.sample('run',0.99,rng); print(round(ph,3), st)" < /dev/null` prints `(3,) 0.018 False` then `1.018 True` and exits 0.
- Depends on: none. Size M.
- Notes: keep `python3 simulate.py` behaviour identical for students.

### T21 Harder simulator: jitter, asymmetry, re-orientation, offline mode
- Problem (Verified on harness): fixed R (simulate.py:6), perfectly periodic cadence (simulate.py:14-15), identical spikes (simulate.py:18); stride asymmetry alone flips 204/286 running windows to WALKING.
- Change: implement `asym` (`a = amp * (1 + asym * (int(phase) % 2))`) and `jitter` (at each new step draw `f_step = f * rng.normal(1, jitter)` until the next step; keep state in a mutable argument or return value). argparse in main: `--asym`, `--jitter` (floats, default 0), `--reorient-every` (seconds, default 0; new R via qr every that many seconds, print `re-oriented` to stderr), `--seconds N` (offline: no HTTP, no toggle thread, print `true steps: N` to stdout, exit 0), `--url`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 simulate.py --seconds 60 < /dev/null | tail -1; python3 simulate.py --seconds 60 --asym 1 --jitter 0.1 --reorient-every 10 2>/dev/null < /dev/null | tail -1` prints exactly `true steps: 108` then `true steps: <n>` with n in 98..118, both exiting 0 with no network access and no traceback on stderr for the first command.
- Depends on: T20. Size M.
- Notes: 20 seeds gave 104..108 (scratchpad/verify-server-demo/t24_t21.py).

### T22 gravity_complementary: default k=0.995 and validate gyro
- Problem (Verified): k=0.98 (orientation.py:21) is noisier than the lowpass without rotation (0.83 vs 0.43 deg walk); k=0.995 gives 0.23/0.17 and 0.23/0.20 under a 30 deg swing (lowpass 18.6/18.7). Wrong-length gyro -> IndexError at orientation.py:29, None -> TypeError, empty acc -> IndexError at :26, deg/s overflows to all-NaN silently. Wrong sign gives 37.8 deg.
- Change: `gravity_complementary(acc, gyro, k=0.995)`: `acc = np.asarray(acc, float); gyro = np.asarray(gyro, float)`; raise ValueError for empty acc, for `gyro.shape != acc.shape`, and for `np.abs(gyro).max() > 35` ('gyro max |w| > 35 rad/s (2000 deg/s): are these deg/s? expected rad/s'). Loop unchanged. Docstring: rad/s body frame, same grid as acc (resample first, T24), sign convention g <- g - (w*dt) x g, k=0.995 ~2 s time constant, 0.2 deg vs 19 deg under a 30 deg swing, 1 deg/s bias costs ~2 deg.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import numpy as np, synth, orientation as o\nfor name, kw in [('walk', {}), ('run', {}), ('walk_swing30', dict(swing_deg=30)), ('run_swing30', dict(swing_deg=30))]:\n    a, n, d, w = synth.make([(name.split('_')[0], 30)], **kw)\n    print(name, round(float(synth.ang_err_deg(o.gravity_complementary(a, w), d)[200:].mean()), 2), round(float(synth.ang_err_deg(o.gravity_lowpass(a), d)[200:].mean()), 2))"` prints complementary errors 0.23, 0.17, 0.23, 0.20 (each within 0.05) and lowpass errors 0.43, 0.31, 18.6, 18.7 (each within 0.1). Then each of these must exit non-zero with ValueError in the traceback: `python3 -c "import numpy as np,orientation as o; o.gravity_complementary(np.zeros((300,3)),np.zeros((10,3)))"`; `python3 -c "import numpy as np,orientation as o; o.gravity_complementary(np.zeros((300,3)),None)"`; `python3 -c "import numpy as np,orientation as o; o.gravity_complementary(np.zeros((300,3)),np.full((300,3),100.0))"`; `python3 -c "import numpy as np,orientation as o; o.gravity_complementary(np.zeros((0,3)),np.zeros((0,3)))"`. Finally `python3 tests/test_orientation.py` prints ok, and `python3 eval_dsp.py | grep -i complementary` still prints a line.
- Depends on: T03. Size S.
- Notes: no caller passes k today. T24 must resample before calling (shape check raises). The 35 rad/s guard is a units sanity check only.

### T23 gravity_lowpass: empty guard, fs parameter, tau_s trade-off + reorient metric
- Problem (Verified): orientation.py:15 on empty input -> IndexError; alpha (orientation.py:13) hard-codes FS; tau trade-off measured: noise 0.84/0.43/0.24/0.13 deg for tau 0.5/1/2/4 s, settle after an 88.6 deg turn 1.26/2.51/5.05/10.14 s, steps after the turn 27/27/25/23 of 27.
- Change: `gravity_lowpass(acc, tau_s=1.0, fs=FS)`: asarray float; ValueError on empty; `alpha = 1 / (1 + tau_s * fs)`; `g[0] = acc[:max(1, int(round(fs)))].mean(axis=0)`. Docstring with the trade-off. In eval_dsp.py replace the reorient line with `reorient settle_s tau0.5=<x.xx> tau1.0=<x.xx> tau2.0=<x.xx> steps_after_turn tau0.5=<n> tau1.0=<n> tau2.0=<n>` computed as scratchpad/dsp/e7_reorient.py: seeds 0 and 7 walk 15 s vstacked; settle = first index after 1500 with error < 5 deg / 100; steps_after_turn = `len(steps.detect_steps(vertical[1500:], 'WALKING'))`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 eval_dsp.py | grep reorient` prints `reorient settle_s tau0.5=1.26 tau1.0=2.51 tau2.0=5.05 steps_after_turn tau0.5=27 tau1.0=27 tau2.0=25` (settle within 0.1 s, steps within 1). `python3 -c "import numpy as np,orientation as o; o.gravity_lowpass(np.zeros((0,3)))"` exits non-zero with ValueError (not IndexError). `python3 -c "import numpy as np,orientation as o; print(o.gravity_lowpass(np.tile([0,0,9.81],(300,1)).astype(float), fs=99.7)[-1].round(3))"` prints `[0.    0.    9.81 ]`. `python3 tests/test_orientation.py` prints ok.
- Depends on: T03, T22. Size M.
- Notes: fs has no caller until something measures a rate (T18 resamples instead).

### T24 server: ingest gyroscope and use gravity_complementary, aligned by sample number
- Problem (Verified): 'gyroscope' packets are dropped (server.py:24-30); state() always uses the lowpass (server.py:41). Synthetic 30 deg swing: live lowpass 18.65 deg off vs 0.42 deg complementary. Trailing-count alignment double-counts (56/54) because acc entries precede gyro entries in a packet.
- Change: `gyr = collections.deque(maxlen=8 * FS)`, `n_gyr = [0]`; in ingest `elif name == 'gyroscope': n_gyr[0] = n_gyr[0] + 1 if n_gyr[0] else n_seen[0] + 1; gyr.append([n_gyr[0], *xyz])`. Clear both in reset_state(). `def _gravity(acc, b, gyr_arr)`: select gyro rows with sample number in [b[0,0], b[-1,0]]; if `sel.sum() >= len(b) - FS // 5 and len(acc) == len(b)`: build `gy` zero-padded by index, `if np.median(np.linalg.norm(gy, axis=1)) > 20: gy = np.radians(gy)`, then `try: return gravity_complementary(acc, gy, k=0.995), 'gyro' / except ValueError: return gravity_lowpass(acc), 'lowpass (gyro rejected)'` (critic: T22's 35 rad/s guard can raise on a deg/s flick with median < 20); otherwise `gravity_lowpass(acc), 'lowpass'`. In _analyse replace the gravity call with `g, source = _gravity(acc, b, gyr_arr)` (gyr_arr copied under the lock) and add `'gravity_source': source` to the ready dict.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import numpy as np,synth,server; from orientation import FS; a,n,d,g=synth.make([('walk',30)],swing_deg=30); errs=[]\nfor i in range(0,len(a),20):\n    server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a[i:i+20]]+[{'name':'gyroscope','values':dict(zip('xyz',v))} for v in g[i:i+20]])\n    s=server.state()\n    if s['ready'] and i>=2*FS: errs.append(np.degrees(np.arccos(abs(np.dot(s['down'],d[i+19])))))\nprint(s['gravity_source'], round(float(np.mean(errs)),2), server.steps['count'], n)"` prints `gyro <e> 54 54` with e below 2.0 (patched copy: 0.42). Sending the gyro entries before the acc entries in each packet must give the same line.
- Depends on: T01, T22, T18. Size M.
- Notes: equal acc/gyro rates assumed (Unverified; T44 checks); late-start offset is an Inference.

### T25a orientation.py: gravity_ok(g) and a norm floor in vertical_horizontal
- Problem (Verified): orientation.py:38 divides by norm(g) with no floor (all-zero g -> NaN). A user-acceleration-only stream gives lowpass |g| ~0.08 and down 82.6 deg wrong with no signal to the caller.
- Change: constants `G_MIN, G_MAX = 5.0, 14.0`; `def gravity_ok(g)`: `n = np.linalg.norm(np.asarray(g, float), axis=1); return G_MIN < float(np.median(n)) < G_MAX`. In vertical_horizontal replace lines 38-40 with `norm = np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-6); down = g / norm; along = np.sum(acc * down, axis=1); vertical = along - norm[:, 0]`. Docstring with measured medians (9.4-9.8 no swing, 7.2 at 60 deg swing, 4.9 at 90 deg, <= 1.1 user-only).
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import numpy as np,synth,orientation as o; a,*_=synth.make([('walk',10)]); g=o.gravity_lowpass(a); print(o.gravity_ok(g), o.gravity_ok(o.gravity_lowpass(a-g))); a6,*_=synth.make([('run',30)],swing_deg=60); print(o.gravity_ok(o.gravity_lowpass(a6))); print(bool(np.isfinite(np.concatenate(o.vertical_horizontal(np.ones((3,3)),np.zeros((3,3)))[:2])).all())); v0,h0,d0=o.vertical_horizontal(a,g); print(float(np.abs(v0).max()>0))"` prints 'True False', 'True', 'True', 'True'. `python3 tests/test_orientation.py` prints ok.
- Depends on: T23. Size S.
- Notes: real arm-swing amplitude Unverified.

### T25b server: refuse to count on implausible gravity; dashboard shows the reason
- Problem (Verified): user-acceleration-only stream -> server.py:39-40 rescales by 9.81, |g| 0.84, 67/54 steps, 12 windows RUNNING; state() never reports it and dashboard.html:30 shows only 'waiting for phone…'.
- Change: import gravity_ok. In state() after `g = gravity_lowpass(acc)` (inside _analyse or right after it): `if not gravity_ok(g): return {"ready": False, "error": f"no gravity: |g| median {np.median(np.linalg.norm(g, axis=1)):.1f} m/s^2 - enable Gravity/TotalAcceleration in Sensor Logger"}`; same early return (no counting) in _count_locked(). dashboard.html: else branch to `if(s.ready){...}`: `else{document.getElementById('tilt').textContent=s.error||'waiting for phone…';}`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth,server,orientation as o; a,*_=synth.make([('walk',10)]); u=a-o.gravity_lowpass(a); server.ingest([{'name':'totalacceleration','time':int(i*1e7),'values':dict(zip('xyz',map(float,v)))} for i,v in enumerate(u)]); s=server.state(); print(s['ready'], s['error'][:10], server.steps['count'])"` prints 'False no gravity 0'. Positive control: `python3 -c "import synth,server; a,*_=synth.make([('walk',10)]); server.ingest([{'name':'totalacceleration','time':int(i*1e7),'values':dict(zip('xyz',map(float,v)))} for i,v in enumerate(a)]); s=server.state(); print(s['ready'], s['state'], server.steps['count']>0)"` prints 'True WALKING True'. `grep -c "s.error" dashboard.html` prints 1.
- Depends on: T25a, T24. Size M.
- Notes: packets carry epoch-ns `time` so the command survives T17/T18.

### T26 Show steps-per-minute from step intervals
- Problem (Verified): spm = round(cadence*60) (server.py:55) from 0.5 Hz FFT bins (steps.py:8-9) -> only 60/90/120/150/180; true rates 108 and 168.
- Change: `steps['idx'] = collections.deque(maxlen=64)`; in _count_locked() append `int(gi)` where `steps['count'] += 1`. `def spm_from_steps(now_idx, feat)`: `recent = [i for i in steps['idx'] if i > now_idx - 10 * FS]`; if len >= 3 return `60 * (len(recent) - 1) / ((recent[-1] - recent[0]) / FS)` else `feat['cadence_hz'] * 60`. state(): `'spm': round(spm_from_steps(idx[-1], feat))`. Clear `steps['idx']` in /reset (under lock) and reset_state(). dashboard.html:34 `cad` line -> `FFT peak ${s.cadence.toFixed(2)} Hz`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth, server\nfor mode in ('walk','run'):\n    server.reset_state(); a,t,*_=synth.make([(mode,60)])\n    for i in range(0,len(a),20): server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a[i:i+20]])\n    print(mode, server.state()['spm'])"` prints `walk <n>` with n in 104..112 and `run <m>` with m in 162..174 (patched copy: 108 and 168; currently prints 120 or 90 for the walk).
- Depends on: T12, T25b (was T25). Size M.
- Notes: keep `cadence` in the JSON for the dashboard dotted line (dashboard.html:43).

### T27 Dashboard shows when the phone or server has gone quiet
- Problem (Verified): state() has no timing key (server.py:33-56); 'waiting for phone…' (dashboard.html:21) never returns after the first ready frame; `catch(e){}` (dashboard.html:46) hides a dead server.
- Change: server.py `import time`; `last_rx = [0.0]` set at the end of ingest() when a sample was accepted; state() returns `'age_s': None if last_rx[0] == 0 else round(time.time() - last_rx[0], 1)` in both dicts; reset in reset_state(). dashboard.html: after the ready block, `const t=document.getElementById('tilt'); if(s.age_s!=null && s.age_s>2){t.textContent=`no data for ${s.age_s.toFixed(0)} s -- is the phone still streaming?`; document.body.style.opacity=.5}else{document.body.style.opacity=1}`; in the catch set tilt to 'server unreachable'.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import server, time; print(server.state()['age_s']); server.ingest([{'name':'totalacceleration','values':{'x':0,'y':0,'z':9.81}}]); time.sleep(1.5); s=server.state(); print(s['ready'], s['age_s'] >= 1.4)"` prints `None` then `False True`; `grep -c 'age_s' dashboard.html` prints at least `1` (currently `0`).
- Depends on: T26. Size M.
- Notes: age_s must be None before the first packet.

### T28 cadence_hz: zero-pad FFT 8x and raise the half-frequency ratio to 0.6
- Problem (Verified): spectrum() (steps.py:8-9) gives 0.5 Hz bins; worst median cadence error 0.5 Hz; the 0.4 half rule (steps.py:21-23) halves asym-1.0 running in 76% and walking in 26% of windows. Removing the rule doubles sharp-strike walking in 57-78% of windows.
- Change: `cadence_hz(x, pad=8, ratio=0.6)`: n = len(x)*pad; `xw = (x - x.mean()) * np.hanning(len(x))`; `f = np.fft.rfftfreq(n, 1/FS)`; `a = np.abs(np.fft.rfft(xw, n))`; band, best, half as today; `ab[half].max() > ratio*ab.max()`. spectrum() untouched (server.py:51, steps.py:29-32 use it). Docstring: resolution 0.0625 Hz; ratio 0.6 rationale. tests/test_steps.py: replace the two 2 s assertions with `abs(cadence_hz(sine(1.8,2))-1.8) < 0.07` and `abs(cadence_hz(sine(2.8,2))-2.8) < 0.07`, drop the 'T28 relaxes this' comment.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import numpy as np; from steps import cadence_hz; t=np.arange(200)/100; print(cadence_hz(np.sin(2*np.pi*1.8*t)), cadence_hz(np.sin(2*np.pi*2.8*t)))"` prints `1.8125 2.8125`; `python3 tests/test_steps.py; echo exit=$?` prints `ok` and `exit=0`; `python3 eval_dsp.py` prints `cadence worst_median_abs_err_hz=0.025`, `halving run2.8_asym1.0=0.0 walk1.8_asym1.0=0.111` and `doubling walk1.8_width0.02=0.0` (each number within 0.02; before the change the same lines read 0.5, 0.759/0.259 and 0.0).
- Depends on: T03, T04, T08 (steps.py serialisation). Size M.
- Notes: classify's 2.35 Hz threshold now sees a continuous cadence (2.3 Hz fast walk becomes WALKING); T39 gives the data to retune.

### T28b tests/test_classify.py: flip the known-fail after T28
- Problem (Verified behaviour, Inference on marker form): after T28 the stride_asym 1.0 run labels 100% RUNNING, so T11's KNOWN-FAIL marker goes stale.
- Change: in tests/test_classify.py remove the known-fail marker for the run stride_asym=1.0 case and replace it with a plain assertion that >= 90% of the 2 s windows of `synth.make([('run',30)], stride_asym=1.0)` classify as RUNNING, using the file's existing window loop. Rename the function test_run_asym; keep the printed line format `PASS run stride_asym=1.0 ...`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 tests/test_classify.py; echo exit=$?` -> output contains a line starting `PASS run stride_asym=1.0`, contains no line with `KNOWN-FAIL`, and ends with `exit=0`. Sanity: `git stash` of the steps.py change from T28 makes the same command report that case failing (24% RUNNING).
- Depends on: T28, T11. Size S.
- Notes: no-op if T11 lands after T28 and writes the case as a plain pass.

### T29 spectrogram.py --synth
- Problem (Verified): README.md:90 and :104 ask for walk-vs-run spectrograms; no code exists; matplotlib not installed; train.py not importable until T07.
- Change: spectrogram.py with argparse `--synth` (required for now) and `--out` (default spectrogram.csv). `acc, true, *_ = synth.make([('walk',20),('run',20)])`; g = gravity_lowpass(acc); v = vertical_horizontal(acc, g)[0]. For s in range(100, len(v)-200, 50): w = v[s:s+200]; f, a = steps.spectrum(w); keep = f <= 8. CSV header `'t_s,' + ','.join(f'{x:.1f}' for x in f[keep])`, rows `f'{s/FS:.2f},' + ','.join(f'{x:.5f}' for x in a[keep])`. Per window print `f't={s/FS:.2f} cadence={c:.3f} ratio2x={ratio2x:.2f}'` with c = steps.cadence_hz(w), ic = argmin|f-c|, i2 = argmin|f-2c|, ratio2x = a[i2]/a[ic]. After the loop try matplotlib (Agg): imshow transposed matrix, overlay cadence and 2x cadence, savefig('spectrogram.png'); on ImportError print `matplotlib not installed, csv only`. Append `spectrogram.csv` and `spectrogram.png` to .gitignore.
- Acceptance: `cd /home/user/qmind-step-detector && python3 spectrogram.py --synth | tee /tmp/spec.log | tail -1` prints `matplotlib not installed, csv only`; `head -1 spectrogram.csv` prints a header starting `t_s,0.0,0.5,1.0` and ending `,8.0`; `wc -l spectrogram.csv` prints `75 spectrogram.csv`; `grep -c '^t=' /tmp/spec.log` prints `74`; `awk -F'[= ]' '/^t=/{ if ($2<=18.5 && ($4<1.5||$4>2.0)) bad++; if ($2>=20 && ($4<2.5||$4>3.0)) bad++ } END{print bad+0}' /tmp/spec.log` prints `0`.
- Depends on: T01, T02 (.gitignore serialisation). Size M.
- Notes: windows at t=19.0/19.5 straddle the switch, hence the ranges. PNG branch Unverified here.

### T29b spectrogram.py: accept a recording folder
- Problem (Verified): T29 is synthetic-only; train.load importable only after T07.
- Change: optional positional `folder` (nargs='?') in a mutually exclusive group with --synth; when given `from train import load; acc = load(folder)`; rest unchanged. One-line usage error if neither.
- Acceptance: `cd /home/user/qmind-step-detector && python3 make_fixtures.py --out data_synth && python3 spectrogram.py data_synth/p1_walk_hand | grep -c '^t='` prints `54`; `wc -l spectrogram.csv` prints `55 spectrogram.csv`; `python3 spectrogram.py data_synth/p1_walk_hand | awk -F'[= ]' '/^t=/ && ($4<1.5||$4>2.0){bad++} END{print bad+0}'` prints `0` (today every window reads 2.0; after T28, 1.75-1.8125).
- Depends on: T29, T07, T02. Size S.
- Notes: 54 windows = range(100, 2800, 50).

### T31 Derive the step min-gap from cadence instead of the label
- Problem (Verified): detect_steps min_gap 0.4 s for non-RUNNING (steps.py:56) caps at 2.5 steps/s; forced-WALKING 3.2 Hz run counts 153/192 live. Fix `clip(0.6/cadence, 0.2, 0.45)` gives 192/192, 168/167 asym run, 108/108 walk, slow 1.4 Hz walk 92 -> 94 (true 83).
- Change: steps.py: `def detect_steps(vertical, state, min_gap_s=None)`; replace steps.py:56 with `min_gap = int(FS * (0.28 if state == "RUNNING" else 0.4)) if min_gap_s is None else int(FS * min_gap_s)`. Add `def gap_from_cadence(c): return float(np.clip(0.6 / max(c, 1e-6), 0.2, 0.45))` with docstring. In count_steps call `detect_steps(v[lo:end], st, min_gap_s=gap_from_cadence(feat['cadence_hz']))`. server.py: import gap_from_cadence (server.py:8) and in `_count_locked()` call `detect_steps(vert[-4 * FS:], st, min_gap_s=gap_from_cadence(feat['cadence_hz']))`; keep looking up `classify` as a server-module global. train.py untouched.
- Acceptance: `cd /home/user/qmind-step-detector && python3 -c "import synth, server, importlib\ndef live(a, force=None):\n    importlib.reload(server)\n    if force: server.classify = lambda feat: force\n    s = None\n    for i in range(0, len(a), 20): server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a[i:i+20]]); s = server.state()\n    return s['steps']\nprint(live(synth.make([('run',60)], f_run=3.2, amp_run=9.0)[0], force='WALKING'), live(synth.make([('walk',60)], f_walk=1.4, amp_walk=2.0)[0]))"` prints `192 94` (pass band: first number in 186..198, currently 153; second number <= 95, true 83, currently 92; verified 192 94 without T28 and 192 93 with T28). Then `python3 -c "import synth, steps; print([round(steps.gap_from_cadence(c),3) for c in (3.2,1.5,0.0)]); a,t,*_=synth.make([('run',60)],seed=3,stride_asym=1.0); print(steps.count_steps(a)[0], t)"` prints `[0.2, 0.4, 0.45]` then `168 167`. `python3 tests/test_steps.py` must still print ok.
- Depends on: T08, T12, T28 (steps.py serialisation). Size M.
- Notes: T30 dropped (its mean-subtraction makes the slow-walk number 96 and fails this gate).

### T32 Tolerant folder-name parsing in build_dataset
- Problem (Verified): train.py:55 raises ValueError for `brett_still` or a loose file; `Brett_Walk_Hand` creates class `Walk`; Finder copy `p1_walk_hand 2` creates placement `hand 2` (printed `placements: ['hand', 'hand 2', 'pocket']`).
- Change: `def parse_name(folder)`: None unless isdir; `name = re.sub(r'\s+\d+$', '', basename.strip().lower())`; parts = name.split('_'); None unless `len(parts) >= 3 and parts[1] in {'walk','run','still'} and parts[2] in {'hand','pocket'}`; else parts[:3]. In build_dataset: `meta = parse_name(folder); if meta is None: print(f'skipping {folder}: name it <person>_<walk|run|still>_<hand|pocket>, e.g. brett_still_hand'); continue`. `import re`.
- Acceptance: `cd /home/user/qmind-step-detector && cp -r data_synth/p1_still_hand data_synth/brett_still && cp -r data_synth/p1_walk_hand data_synth/Brett_Walk_Hand && cp -r data_synth/p1_walk_hand 'data_synth/p1_walk_hand 2' && echo hi > data_synth/notes.txt && python3 train.py data_synth > /tmp/t32.txt; echo exit=$?; grep -c '^skipping' /tmp/t32.txt; grep windows /tmp/t32.txt; rm -rf data_synth/brett_still data_synth/Brett_Walk_Hand 'data_synth/p1_walk_hand 2' data_synth/notes.txt` prints `exit=0`, then `2`, then `1084 windows from 5 people, placements: ['hand', 'pocket']`.
- Depends on: T07. Size S.
- Notes: 2-part names skipped on purpose.

### T33 train.load() fails clearly, folder skipped
- Problem (Verified): both CSVs absent -> read() returns None and train.py:30 raises TypeError; no column check (train.py:31,33); case-sensitive lookup (train.py:25). Real iOS header is `time,seconds_elapsed,z,y,x`.
- Change: in load(): `files = {basename.lower(): path for *.csv}`; look up totalacceleration.csv / accelerometer.csv / gravity.csv; raise `FileNotFoundError(f'{folder}: need TotalAcceleration.csv or Accelerometer.csv + Gravity.csv')`; lower-case columns, require x,y,z else `ValueError(f'{path}: columns {list(df.columns)} lack x,y,z')`; drop non-finite rows; `ValueError(f'{folder}: only {len(acc)} usable rows, need > {3*FS}')` when `len(acc) <= 3*FS`. In build_dataset wrap load in `try/except (FileNotFoundError, ValueError) as e: print('skipping', e); continue`.
- Acceptance: `cd /home/user/qmind-step-detector && mkdir -p data_synth/p9_walk_hand && printf 'x,y\n1,2\n' > data_synth/p8_run_pocket.csv && python3 train.py data_synth > /tmp/t33.txt; echo exit=$?; grep -c '^skipping' /tmp/t33.txt; grep -c 'need TotalAcceleration.csv' /tmp/t33.txt; grep -c 'Leave-one-placement-out' /tmp/t33.txt; rm -rf data_synth/p9_walk_hand data_synth/p8_run_pocket.csv` prints `exit=0`, `2`, `1`, `1`, and the summary line still reads 976 windows.
- Depends on: T32. Size S.
- Notes: unit scaling (train.py:34-35) left as is.

### T34 train.py: confusion and per-fold accuracy; survive single-value splits
- Problem (Verified): train.py:71-73 prints only the mean; A's 89% is 107/272 run windows -> walk in the held-out-hand fold; C's 94% is 61/432 walk -> still in the held-out-pocket fold. train.py:68-70 crashes (`Found array with 0 sample(s)`) with one person.
- Change: in evaluate(): `from sklearn.metrics import confusion_matrix`; `LABELS = ['still','walk','run']`; if `df[split].nunique() < 2`: print `skipping leave-one-{split}-out: only one {split}` and continue. Accumulate `cm` over folds, `fold_acc[held] = f'{acc:.0%}'`. Print per model `  A  raw x/y/z  mean 89%  per-fold {'hand': '78%', 'pocket': '100%'}` and rows `    true still | 272 0 0`, `    true walk  | ...`, `    true run   | ...`. Keep the mean and n_estimators=200.
- Acceptance: `cd /home/user/qmind-step-detector && python3 train.py data_synth` prints, in the Leave-one-placement-out block, for A `per-fold {'hand': '78%', 'pocket': '100%'}` and a `true run` row `0 107 165`; for C `per-fold {'hand': '100%', 'pocket': '88%'}` and a `true walk` row `61 371 0`; every confusion table's rows sum to 272, 432, 272. Then: `mkdir -p one && cp -r data_synth/p1_* one/ && python3 train.py one; echo exit=$?; rm -rf one` prints a line `skipping leave-one-person-out: only one person`, a placement block, and `exit=0`.
- Depends on: T07, T33 (train.py serialisation). Size M.
- Notes: after T35 the 61-row table is D and the 6-feature C shows 58.

### T35 A/B/C like-for-like: C vertical-only (6), D vertical+horizontal (7)
- Problem (Verified): train.py:47-48 strip h_std from A and B but train.py:49 keeps it for C. B is orientation-invariant and scores 100% vs C 94%, contradicting README.md:105. h_std is a placement fingerprint (walk-hand 1.40 vs walk-pocket 0.24).
- Change: windows() yields A, B, `D = features(v[w], h[w])`, `C = {k: val for k, val in D.items() if k != 'h_std'}`; add D to the row dict; loop `for name in 'ABCD'` with labels {'A': 'raw x/y/z (18 feats)', 'B': 'magnitude only (6)', 'C': 'vertical only (6)', 'D': 'vertical + horizontal (7)'}; print the legend `A vs B/C/D: does orientation-independence matter?  B vs C: does knowing the direction of motion help?  C vs D: does the horizontal channel help?`; update the docstring lines 7-10.
- Acceptance: `cd /home/user/qmind-step-detector && python3 train.py data_synth | grep -E '^  [ABCD] '` prints 8 lines with the feature counts in parentheses; in the placement block B reads `mean 100%`, C `mean 94%`, D `mean 94%`, and the C confusion `true walk` row reads `58 374 0` while D's reads `61 371 0`.
- Depends on: T34. Size S.
- Notes: on this simulator B >= C; T41 documents it.

### T36 ablation.py
- Problem (Verified): nobody knows which steps.features keys (steps.py:33-39) carry placement vs activity information. Measured LOPO (100 trees): D 93.8%; adding hv_ratio/vh_corr/v_band_frac drops to ~79%; single-feature v_std 100%, h_std 42%; dropping v_p2p 75.7%.
- Change: ablation.py importing `load, parse_name, WIN` from train, `features, cadence_hz, spectrum` from steps, `gravity_lowpass, vertical_horizontal, FS` from orientation. `extra_features(v, h)`: hv = h - h.mean(); {'hv_ratio': h.std()/(v.std()+1e-6), 'h_cadence': cadence_hz(hv), 'vh_corr': corrcoef(v, hv)[0,1] if both std > 1e-6 else 0.0, 'v_skew': ((v-v.mean())**3).mean()/(v.std()**3+1e-9), 'v_band_frac': E_v(1-4 Hz)/(E_v+E_h) from spectrum() amplitudes squared}. Rows per folder (parse_name, load, v/h once, `s in range(FS, len(acc)-WIN, FS//2)`). `lopo(cols)`: mean accuracy over held-out placements, RandomForestClassifier(n_estimators=100, random_state=0). Print `D (7 base) acc: 94%`, table 1 (7 rows: feature drop_acc only_acc importance), table 2 (5 rows: feature add_acc only_acc). Usage `python3 ablation.py <data_dir>`.
- Acceptance: `cd /home/user/qmind-step-detector && python3 ablation.py data_synth; echo exit=$?` prints `D (7 base) acc: 94%`, a 7-row table and a 5-row table (12 feature rows) with numeric columns, and `exit=0`; in table 1 `only_acc` for v_std is 100% and for h_std is below 50% (measured 42%), `drop_acc` for h_std is 94% and for v_p2p is 76%; in table 2 `add_acc` for hv_ratio is below 85% (measured 79%) and for v_skew is at least 93%.
- Depends on: T32. Size M.
- Notes: figures from scratchpad/verify-classify-ml/exp_ablation.py, exp_addone.py.

### T37 Save the trained D model to model.joblib
- Problem (Verified): train.py:70 fits inside the fold loop and discards; feature order is dict insertion order (steps.py:33-39) flattened at train.py:66; classes_ are ['run','still','walk'].
- Change: `def save_model(df, path)`: `feature_names = list(df['D'].iloc[0].keys())`; `X = pd.DataFrame(list(df['D']))[feature_names].values`; fit RandomForestClassifier(n_estimators=100, random_state=0) on all rows; `joblib.dump({'model': m, 'features': feature_names, 'labels': {'still':'STILL','walk':'WALKING','run':'RUNNING'}, 'n_windows': len(df)}, path)`; print `saved {path}: {len(df)} windows, classes {sorted(m.classes_)}`. Main guard: `args = [a for a in sys.argv[1:] if not a.startswith('--')]`; `data_dir = args[0] if args else <default data/>`; `save = ('--save' in sys.argv) or not args`. Default path next to train.py. Add `joblib` to requirements.txt.
- Acceptance: `cd /home/user/qmind-step-detector && python3 train.py data_synth --save | tail -1 && python3 -c "import joblib; d=joblib.load('model.joblib'); print(sorted(d['model'].classes_), d['features'], d['labels']['run'], d['n_windows'])"` prints a line starting `saved ` and ending `976 windows, classes ['run', 'still', 'walk']`, then `['run', 'still', 'walk'] ['cadence_hz', 'v_std', 'h_std', 'v_p2p', 'e_walk_band', 'e_run_band', 'e_high'] RUNNING 976`. `rm model.joblib && python3 train.py data_synth | grep -c '^saved'` prints `0`.
- Depends on: T35. Size M.
- Notes: a synthetic-trained model must not be the demo model; G08 git-ignores model.joblib. Leave model.joblib present for T38's acceptance, then remove it before running T10b's rule-based expectations.

### T38 steps.classify loads model.joblib with label mapping and rule fallback
- Problem (Verified): classify (steps.py:42-46) returns 'STILL'/'RUNNING'/'WALKING'; dashboard.html:14,33-34 and detect_steps (steps.py:54-56) depend on those strings; a model predicts 'walk'/'run'/'still'. T04's test_classify passes partial dicts.
- Change: `MODEL_PATH = os.path.join(dirname(abspath(__file__)), 'model.joblib')`, `_model = [None]`. `def load_model(path=MODEL_PATH)`: import joblib inside; set `_model[0]` to the loaded dict if the file exists else None; import-time call wrapped in try/except printing `steps: model not loaded ({e}); using rule`. Rename the rule to `classify_rule(feat)`. `classify(feat)`: `d = _model[0]`; rule if None; else `x = np.array([[float(feat[k]) for k in d['features']]])`; `return d['labels'][str(d['model'].predict(x)[0])]`. tests/test_steps.py: test_classify uses classify_rule; add test_classify_model (skip if `_model[0]` is None; else full 7-key run dict -> RUNNING, still dict -> STILL).
- Acceptance: With model.joblib present from T37's acceptance: `cd /home/user/qmind-step-detector && python3 -c "from steps import classify, classify_rule; f={'cadence_hz':3.0,'v_std':2.5,'h_std':0.3,'v_p2p':12,'e_walk_band':0.01,'e_run_band':0.6,'e_high':0.3}; print(classify(f), classify_rule(f))"` prints `RUNNING RUNNING`. Then `mv model.joblib /tmp/m.bak && python3 -c "from steps import classify; print(classify({'cadence_hz':1.0,'v_std':0.1,'h_std':0.1,'v_p2p':0.3,'e_walk_band':0.1,'e_run_band':0.1,'e_high':0.5}))"; mv /tmp/m.bak model.joblib` prints `STILL` with no traceback. `python3 tests/test_steps.py; echo exit=$?` ends with `exit=0`. Finally `python3 -c "import synth, server; a,t,*_=synth.make([('walk',60)]); st=set()\nfor i in range(0,len(a),20):\n    server.ingest([{'name':'totalacceleration','values':dict(zip('xyz',v))} for v in a[i:i+20]]); s=server.state()\n    if s.get('ready'): st.add(s['state'])\nprint(t, server.steps['count'], st)"` prints `108 108 {'WALKING'}`.
- Depends on: T37, T04, T28, T31 (steps.py and tests/test_steps.py serialisation). Size M.
- Notes: single-row predict 5.9 ms; dashboard polls at 200 ms. Keep classify_rule exported (T11, T39, G09).

### T39 thresholds_report.py
- Problem (Verified): steps.py:44-46 hard-codes 0.4 / 2.35 / 5; with 0.5 Hz bins `> 2.35` is `>= 2.5`; `v_std > 5` never fires on synthetic (run v_std max 3.75); still v_std max 0.056 vs walk min 0.84. Real values Unverified.
- Change: `from train import build_dataset`; `rule = getattr(steps, 'classify_rule', steps.classify)`; `df = build_dataset(sys.argv[1])`; `col = 'D' if 'D' in df else 'C'`; DataFrame of features with activity/placement. Print per-activity quantiles (0, 5, 50, 95, 100%) of v_std and cadence_hz; `rule accuracy overall: NN%` and per activity with MAP={'still':'STILL','walk':'WALKING','run':'RUNNING'}; fit DecisionTreeClassifier(max_depth=2, random_state=0) on [v_std, cadence_hz], print export_text and its LOPO accuracy. Do not change steps.py.
- Acceptance: `cd /home/user/qmind-step-detector && python3 thresholds_report.py data_synth; echo exit=$?` prints quantile rows for still/walk/run where still v_std max is below 0.1 (measured 0.056) and run v_std 50% is between 2 and 4 (measured 2.58), four lines `rule accuracy ...: 100%`, a tree block containing `v_std <=` (measured split at 0.45 then 1.67), a tree LOPO accuracy of 100%, and `exit=0`. Optional after T10a: `python3 make_fixtures.py --out data_hard --hard && python3 thresholds_report.py data_hard` prints `rule accuracy run:` below 85% (measured 79%) with the unmodified cadence_hz; expected to rise after T28.
- Depends on: T07. Size M.
- Notes: whether real running gives v_std > 5 is Unverified.

### T40 README: which URL, .true_steps, 127.0.0.1 fallback (keep the clone URL)
- Problem (Verified): README.md:40 says 'Open the URL that server.py prints' but server.py:86-87 prints two; simulate.py:2 claims to print the count but writes `.true_steps` (simulate.py:25); server.py:85 prints 127.0.0.1 here. The clone URL (README.md:35) is correct: this checkout is a fork of James-Cawse/qmind-step-detector (gh api).
- Change: (1) README.md:40 -> 'Open the Dashboard URL that `server.py` prints (http://localhost:8000); the other URL is the push URL for the phone.' (2) add '`simulate.py` writes the true step count to a hidden file `.true_steps` next to it once a second; run `cat .true_steps` and compare with the dashboard.' (3) section 6 step 4: 'If the printed push URL starts with 127. or says localhost, your laptop has no LAN address yet: use the hotspot IP shown by `ifconfig` (Mac) / `ipconfig` (Windows) in its place.' Do not change the clone URL or simulate.py.
- Acceptance: `cd /home/user/qmind-step-detector && grep -c 'James-Cawse' README.md; grep -c 'Dashboard URL' README.md; grep -c 'true_steps' README.md; grep -c 'ipconfig' README.md` -> prints `1`, `1`, `1`, `1` on four lines (currently `1`, `0`, `0`, `0`); the first line must stay `1`.
- Depends on: none. Size S.
- Notes: if T20 lands first, reword (2) to mention the terminal line too.

### T41 README: what A/B/C/D can prove; synthetic train command
- Problem (Verified): README.md:13 and :105 promise the experiment proves orientation matters, but B is orientation-invariant and scores 100% vs C 94% on synthetic data; README gives no way to run train.py without recordings.
- Change: (1) replace the three bullets at README.md:14-16 with the four variants using train.py's printed labels after T35. (2) paragraph starting 'What this shows:' -- 'A vs the rest tests whether orientation-independence matters (expect a large gap). B vs C tests whether knowing the direction of motion helps the classifier (may be small or zero: magnitude is also orientation-free). C vs D tests whether the horizontal part adds anything. If B >= C, the honest claim is that orientation gives a signed vertical signal for step counting and the vertical/horizontal split, not better classification.' (3) README.md:105 -> 'A vs B vs C vs D: what orientation does and does not buy (see What this shows).' (4) after README.md:40: 'No phone yet? `python3 make_fixtures.py --out data_synth && python3 train.py data_synth` trains on synthetic recordings.' Do not touch train.py.
- Acceptance: `cd /home/user/qmind-step-detector && grep -c '^   - [ABCD]' README.md` prints `4` (currently `3`); `grep -c 'What this shows' README.md` prints `1`; `grep -c 'make_fixtures' README.md` prints a number >= 1; and the quoted command `python3 make_fixtures.py --out data_synth && python3 train.py data_synth` exits 0 from the repo root.
- Depends on: T35, T40. Size S.
- Notes: the signed-vertical claim is an Inference, written as a conditional.

### T42 README: gyro answer with eval_dsp numbers; list synth.py / eval_dsp.py
- Problem (Verified): README.md:89 asks whether the gyro version is steadier with no way to find out; files table (README.md:20-27) lacks synth.py/eval_dsp.py. Measured: lowpass vs complementary(k=0.995) walk 0.43/0.23, run 0.31/0.17, swing30 18.60/0.23 and 18.73/0.20 deg.
- Change: (1) two rows after the simulate.py row: '| `synth.py` | Synthetic walk/run/still with true steps, true down and gyro, for testing without a phone |' and '| `eval_dsp.py` | Cadence, half-rule and down-direction metrics on synthetic data (`python3 eval_dsp.py`) |'. (2) after README.md:92 a paragraph: 'Run `python3 eval_dsp.py`. On synthetic data the gyro fusion only wins when the phone rotates: with a 30 deg arm swing the lowpass down estimate is off by about 19 deg and the complementary filter by about 0.2 deg; without rotation both are below 0.5 deg. A real hand-held recording with Gyroscope enabled is still needed to confirm this.' Paste the numbers eval_dsp.py actually prints, one decimal. No task ids in the README.
- Acceptance: `cd /home/user/qmind-step-detector && grep -c 'eval_dsp.py' README.md` prints a number >= 2 (currently `0`); `grep -c 'synth.py' README.md` prints a number >= 1 (currently `0`); and `python3 eval_dsp.py` exits 0 and prints the down-direction error lines whose numbers the new paragraph quotes.
- Depends on: T03, T22, T41. Size S.
- Notes: depends on T22 so the complementary numbers are the k=0.995 ones.

### T43 README: 'Measure accuracy' section
- Problem (Verified): README.md:92 gives no command for the 3% target; files table lacks evaluator/fixtures/tests; README.md:51 does not say steps.txt is a bare integer; .gitignore (3 lines) would let `git add -A` (README.md:77) commit data_synth unless T02's line is present.
- Change: (1) rows '| `make_fixtures.py` | Synthetic recordings in the Sensor Logger folder layout, with steps.txt |', '| `evaluate.py` | Counted vs true steps per recording, 3% gate |', '| `tests/` | Regression tests: `python3 tests/run.py` |'. (2) README.md:51: steps.txt contains only the integer count, e.g. `echo 50 > steps.txt`. (3) section '## 7. Measure accuracy' after section 6 listing, each with its expected output copied from a real run: `python3 make_fixtures.py --out data_synth --hard`, `python3 evaluate.py --data data_synth` (ends with the `overall:` line; the --hard recordings pass the 3% gate at +0.8%, 26/26 -- do NOT write that they are expected to fail, the critic measured that claim false), `python3 evaluate.py --data data` once real recordings exist, `python3 tests/run.py` (exit 0). (4) grep .gitignore first; add `data_synth*/` only if absent. Under 30 README lines.
- Acceptance: `cd /home/user/qmind-step-detector && grep -c 'evaluate.py' README.md` prints a number >= 3 (currently `0`); `grep -c '## 7. Measure accuracy' README.md` prints `1`; `python3 make_fixtures.py --out data_synth --hard && python3 evaluate.py --data data_synth | tail -1 | grep -c '^overall'` prints `1`; `python3 tests/run.py; echo $?` ends with `0`; `git status --porcelain | grep -c data_synth` prints `0`.
- Depends on: T10a, T10b (was T10), T06, T42. Size M.
- Notes: after T10b, `tail -1` is the `label accuracy:` line, so use `grep -c '^overall'` on the full output instead of `tail -1 | grep`. G08 later points section 7 at `./check.sh`.

### T44 Record one hand-held walk with Gyroscope on; confirm units, sign and lowpass-vs-gyro error (needs_human)
- Problem (Unverified): on a real phone nothing confirms Gyroscope.csv is rad/s (sl/UNITS.md:39, community docs), that its sign matches orientation.py:30, that gyro and acc share a time grid (sl/README.md:334-358 says interpolate), or that a real arm swing moves the lowpass estimate by tens of degrees. README.md:89 asks exactly this. data/ is empty.
- Change: Human: 60 s hand-held walk, Accelerometer + Gravity + Gyroscope at 100 Hz, export CSV, unzip to data/<name>_walk_hand/ with steps.txt. Agent: gyro_check.py (<= 40 lines) taking a folder: `acc = train.load(folder)`; ta = seconds_elapsed of the acceleration CSV; gy = Gyroscope.csv; `gyro = np.column_stack([np.interp(ta, gy.seconds_elapsed, gy[c]) for c in 'xyz'])[:len(acc)]`; ref = Gravity.csv interpolated the same way; print median |gyro|, measured rate `1/median(diff(ta))`, and mean angular errors vs ref for t >= 2 s via synth.ang_err_deg: gravity_lowpass(acc), gravity_complementary(acc, gyro), gravity_complementary(acc, -gyro). Paste the printed lines into the README Orientation paragraph (T42), say which sign won; if -gyro wins add a note that T24 must negate the gyro.
- Acceptance: `cd /home/user/qmind-step-detector && python3 gyro_check.py data/*_walk_hand` prints: 'gyro median |w| = <v> rad/s' with v below 20; 'acc rate = <r> Hz'; and 'down error deg: lowpass=<a> complementary(+gyro)=<b> complementary(-gyro)=<c>' where all three are below 90 and min(b, c) < a. The README Orientation row then contains those numbers. Exit code 0.
- Depends on: T22, T42, T43 (README serialisation). Size M. needs_human=true.
- Notes: the recording itself can happen in wave 0; only the script and README edit wait. Gravity.csv is CoreMotion's fused estimate, not ground truth.

### G01 make_fixtures.py --layout ios
- Problem (Verified): T02 writes only TotalAcceleration.csv; the all-iPhone team exports Accelerometer.csv + Gravity.csv with header `time,seconds_elapsed,z,y,x` and the opposite sign (sl/UNITS.md:18-24); train.py:28-31's iOS branch is exercised by no task. Verified: 24 iOS-layout fixtures give the identical 880 counted steps; vertical_horizontal is invariant to the global sign flip.
- Change: `write_recording(folder, acc, true_steps, layout='android', true_down=None)`: for 'ios', `grav = -9.80665 * true_down`, `user = -acc - grav`; write Accelerometer.csv from user and Gravity.csv from grav with columns exactly `time,seconds_elapsed,z,y,x`; no TotalAcceleration.csv. Add `--layout {android,ios}`; main loop unpacks `acc, true, down, _ = make(...)` and passes `true_down=down, layout=args.layout`; --hard folders use the same flag. ~15 lines.
- Acceptance: `cd /home/user/qmind-step-detector && rm -rf data_synth_ios && python3 make_fixtures.py --out data_synth_ios --layout ios && ls data_synth_ios/p1_walk_hand && head -1 data_synth_ios/p1_walk_hand/Accelerometer.csv && python3 evaluate.py --data data_synth_ios | grep '^overall'` -> prints `Accelerometer.csv`, `Gravity.csv`, `steps.txt`, `time,seconds_elapsed,z,y,x`, then `overall: true=872 counted=880 err=+0.9%  24/24 recordings within 3%`. `ls data_synth_ios/p1_walk_hand | grep -c Total` prints `0`. `python3 train.py data_synth_ios | head -1` starts with `976 windows`.
- Depends on: T10a, T09. Size S.
- Notes: regression fixture for T33 and G02; re-run after each. .gitignore `data_synth*/` (T02) covers it.

### G02 train.load: timestamps, Gravity interpolation, resample when off by > 5%
- Problem (Verified): train.load ignores time columns and pairs Accelerometer/Gravity by position (train.py:30-31) though sl/README.md:114,334-358 says streams do not align. 50 Hz copy of p1_walk_hand counts 41/54 and reads RUNNING; interpolation restores 54/54.
- Change: in load() (after T33) read `t = df['seconds_elapsed']` (fallback `time/1e9`, then `arange/FS`); stable sort by t, drop non-increasing rows; iOS branch interpolates Gravity onto accelerometer times (`np.interp` per axis) instead of `min(len)`; `rate = (len(t)-1)/(t[-1]-t[0])`; if `abs(rate-FS)/FS > 0.05`: grid at 1/FS, interp each axis, print `f'warning: {folder}: {rate:.1f} Hz, resampled to {FS} Hz'`. g-unit rescale after resampling. Expose `def sample_rate(folder)`. ~25 lines.
- Acceptance: `cd /home/user/qmind-step-detector && python3 make_fixtures.py --out data_synth && rm -rf data_synth_50 && mkdir -p data_synth_50/p1_walk_hand data_synth_50/p1_run_pocket && for n in p1_walk_hand p1_run_pocket; do python3 -c "import pandas as pd; pd.read_csv('data_synth/$n/TotalAcceleration.csv').iloc[::2].to_csv('data_synth_50/$n/TotalAcceleration.csv', index=False)"; cp data_synth/$n/steps.txt data_synth_50/$n/; done && python3 -c "from train import load; print(len(load('data_synth_50/p1_walk_hand')), len(load('data_synth/p1_walk_hand')))" && python3 evaluate.py --data data_synth_50 | grep -E 'p1_|overall'` -> prints `warning: data_synth_50/p1_walk_hand: 50.0 Hz, resampled to 100 Hz` then `2998 3000`, then (one warning line per folder) rows `p1_run_pocket            true=  55 counted=  55 err=  +0.0% ok` and `p1_walk_hand             true=  54 counted=  54 err=  +0.0% ok` (with T10b's ` label=...` suffix when present) and `overall: true=109 counted=109 err=+0.0%  2/2 recordings within 3%`. Before the change the same rows read `counted=  27` and `counted=  41`.
- Depends on: T33, T09, T37 (train.py serialisation). Size S.
- Notes: whether iPhones deliver exactly 100 Hz is Unverified (T44 prints it).

### G03 check_recording.py pre-flight
- Problem (Verified): nothing tells a recorder whether their folder is usable before train.py/evaluate.py; no task reads Metadata.csv. Fixture numbers: p1_walk_hand 3000 rows, 30.0 s, median |a| 9.44, steps.txt 54, rate 100.0.
- Change: check_recording.py (<= 45 lines), `python3 check_recording.py FOLDER [FOLDER...]`. Per folder: `files: [...]` (PROBLEM unless totalacceleration.csv or accelerometer.csv+gravity.csv); `columns: [...]` (PROBLEM unless x,y,z after lower-casing); `rate: {..:.1f} Hz  rows: {n}  duration: {..:.1f} s` from seconds_elapsed (PROBLEM outside 90-110 Hz or < 10 s); `median |a|: {..:.2f} m/s^2` from train.load (PROBLEM outside orientation.G_MIN/G_MAX, local 5.0/14.0 fallback); `steps.txt: {n}` or PROBLEM `steps.txt missing or not an integer (write e.g. echo 50 > steps.txt)`; Metadata.csv platform/sampleRateMs/standardisation if present; folder name via train.parse_name (fallback split check). End `OK {folder}` or `PROBLEM {folder}: <first problem>`; exit 1 if any problem.
- Acceptance: `cd /home/user/qmind-step-detector && python3 make_fixtures.py --out data_synth && python3 check_recording.py data_synth/p1_walk_hand; echo exit=$?` -> prints `files: ['TotalAcceleration.csv']`, `columns: ['time', 'seconds_elapsed', 'x', 'y', 'z']`, `rate: 100.0 Hz  rows: 3000  duration: 30.0 s`, `median |a|: 9.44 m/s^2`, `steps.txt: 54`, `OK data_synth/p1_walk_hand`, `exit=0`. Then `mkdir -p /tmp/bad_walk_hand && cp data_synth/p1_walk_hand/TotalAcceleration.csv /tmp/bad_walk_hand/ && echo fifty > /tmp/bad_walk_hand/steps.txt && python3 check_recording.py /tmp/bad_walk_hand; echo exit=$?` ends with a line starting `PROBLEM /tmp/bad_walk_hand: steps.txt` and `exit=1`.
- Depends on: T33, T25a, T02. Size M.
- Notes: print the rate before calling load() so G02's warning does not interleave.

### G04 simulate.py --ios, --seed, --dump, 0.2 s timestamped batches
- Problem (Verified): simulate.py sends one untimestamped totalacceleration sample per POST (simulate.py:22-23); iOS streams accelerometer+gravity in batched packets with epoch-ns `time` (sl/PUSHING.md:22-38), so the rehearsal never exercises server.py:27-28, T16, T17 or T18. Measured: 300 packets of 20 gravity+accelerometer pairs count 108/108 with fs_measured 100.0.
- Change: in main() (after T21): accumulate and POST one packet every `--batch-s` seconds (default 0.2); every entry gets `'time': t_start_ns + i * 10_000_000`. `--ios`: per sample emit gravity `R.T @ [0,0,9.81]` then accelerometer `R.T @ (world - [0,0,9.81])`. `--seed INT` for rng. `--dump FILE`: write each packet as one JSON line `{'messageId': k, 'payload': [...]}` instead of POSTing, no sleep, no toggle thread; usable with `--seconds`; print `true steps: N` at the end.
- Acceptance: `cd /home/user/qmind-step-detector && python3 simulate.py --seconds 60 --ios --seed 1 --dump /tmp/pk.jsonl < /dev/null | tail -1 && wc -l < /tmp/pk.jsonl && python3 -c "import json, server; p=json.loads(open('/tmp/pk.jsonl').readline()); print(len(p['payload']), sorted({e['name'] for e in p['payload']}), isinstance(p['payload'][0]['time'], int)); [server.ingest(json.loads(l)['payload']) for l in open('/tmp/pk.jsonl')]; s=server.state(); print(server.n_seen[0], s['state'], round(s['fs_measured']), abs(server.steps['count']-108)<=3)"` -> prints `true steps: 108`, `300`, `40 ['accelerometer', 'gravity'] True`, `6000 WALKING 100 True`; the dump run finishes in under 5 s.
- Depends on: T21, T17. Size M.
- Notes: plain `python3 simulate.py` keeps today's behaviour apart from batching.

### G05 server.py --port / --public-url and a README tunnel section
- Problem (Verified): decisions.md item 3 asks for a public-URL fallback; server.py:11 hard-codes PORT=8000 and prints only a LAN URL (server.py:85-87); no cloudflared/ngrok here.
- Change: `__main__` (after T19): argparse `--port INT` (default 8000), `--public-url URL`; bind to the port; print `Sensor Logger push URL:  {public_url.rstrip('/')}/data` when given else the LAN form; print `Dashboard:               http://localhost:{port}`. README: after section 6 step 4 add '### 6b. No shared hotspot? Public URL fallback' (<= 12 lines): `cloudflared tunnel --url http://localhost:8000`, copy the trycloudflare URL, `python3 server.py --public-url https://....trycloudflare.com`, paste the push URL into Sensor Logger; one phone per server, not serverless.
- Acceptance: `cd /home/user/qmind-step-detector && (python3 server.py --port 8123 --public-url https://example.trycloudflare.com > /tmp/srv.log 2>&1 &) && sleep 2 && curl -s localhost:8123/state && echo && head -2 /tmp/srv.log && pkill -f 'server.py --port 8123'` -> prints a JSON line starting `{"ready": false`, then `Sensor Logger push URL:  https://example.trycloudflare.com/data` and `Dashboard:               http://localhost:8123`; `grep -c trycloudflare README.md` prints at least `2`; `python3 server.py --help` exits 0.
- Depends on: T19, T27, T43. Size M.
- Notes: tunnel command Unverified here; the phone-on-cellular check goes into G10's session.

### G06 STEPS_MODEL env var; evaluate.py prints the classifier
- Problem (Verified): after T38 evaluate.py's labels depend on whether model.joblib exists (dave_run_pocket label 30% with the rule, 100% with the model; counts unchanged).
- Change: steps.py: in load_model resolve `path = os.environ.get('STEPS_MODEL', MODEL_PATH) if path is None else path` (change the default to None); empty string or missing file -> rule; store `d['path']`. `def model_info()`: None if no model else `f"{os.path.basename(d['path'])} ({d['n_windows']} windows)"`. evaluate.py: print `classifier: {steps.model_info() or 'rule'}` as the first line.
- Acceptance: `cd /home/user/qmind-step-detector && python3 train.py data_synth --save > /dev/null && python3 evaluate.py --data data_synth | head -1 && STEPS_MODEL= python3 evaluate.py --data data_synth | head -1 && STEPS_MODEL=/nonexistent python3 evaluate.py --data data_synth | head -1` -> prints `classifier: model.joblib (976 windows)`, `classifier: rule`, `classifier: rule`. Then with the --hard fixtures: `STEPS_MODEL= python3 evaluate.py --data data_synth | grep dave_run` shows `label= 30%` before T28 and `label=100%` after it, while `python3 evaluate.py --data data_synth | grep dave_run` (model present) shows `label=100%` in both cases; step counts are `counted= 168` in all four runs.
- Depends on: T38, T15, T10b. Size M.
- Notes: optionally tests/run.py sets `os.environ.setdefault('STEPS_MODEL', '')` before importing tests.

### G07 /state and dashboard show which classifier is live
- Problem (Verified): after T38 the swap is invisible: state() (server.py:54-56) carries no source; dashboard.html:20 shows only the label.
- Change: server.py `from steps import model_info`; add `'classifier': model_info() or 'rule'` to both state() dicts. dashboard.html: `<div class="sub" id="clf">&nbsp;</div>` after the `cad` div; in tick() set `document.getElementById('clf').textContent='via '+s.classifier` in the ready branch and the T25b else branch.
- Acceptance: `cd /home/user/qmind-step-detector && python3 train.py data_synth --save > /dev/null && python3 -c "import server; print(server.state()['classifier'])" && STEPS_MODEL= python3 -c "import server; print(server.state()['classifier'])" && grep -c 's.classifier' dashboard.html` -> prints `model.joblib (976 windows)`, `rule`, `2`. `python3 tests/test_server.py` still prints `ok`. Remove model.joblib afterwards.
- Depends on: G06, T27, G05 (server.py serialisation). Size M.
- Notes: the demo model must come from `python3 train.py` on real data/.

### G08 check.sh one-command gate; git-ignore model.joblib
- Problem (Verified): seven separately run checks and no single command; model.joblib (~92 KB) would be committed by `git add -A` (README.md:77). Component timings sum to ~13 s.
- Change: check.sh (`set -euo pipefail`, `cd "$(dirname "$0")"`, chmod +x): `python3 tests/run.py`; `python3 eval_dsp.py`; `python3 make_fixtures.py --out data_synth --hard`; `STEPS_MODEL= python3 evaluate.py --data data_synth`; `python3 train.py data_synth` (T37 saves only with --save, so no backup wrapper needed; keep the backup/restore wrapper from the task text only if T37 landed with save-by-default). Then `DATA=${1:-}`; if set: `shopt -s nullglob; folders=("$DATA"/*/)`; empty -> `echo "no recordings in $DATA"; exit 2`; else `python3 check_recording.py "${folders[@]}"; python3 evaluate.py --data "$DATA"; python3 train.py "$DATA"`. `echo CHECK OK`. Append `model.joblib` to .gitignore. Point README section 7 at `./check.sh` / `./check.sh data` (one line).
- Acceptance: `cd /home/user/qmind-step-detector && ./check.sh > /tmp/check.log 2>&1; echo exit=$?; tail -1 /tmp/check.log; ./check.sh data > /tmp/check2.log 2>&1; echo exit=$?; tail -1 /tmp/check2.log; grep -c '^model.joblib$' .gitignore` -> prints `exit=0`, `CHECK OK`, `exit=2`, `no recordings in data`, `1`. Each run finishes in under 30 s. `touch model.joblib.real && cp model.joblib.real model.joblib; ./check.sh > /dev/null; cmp model.joblib model.joblib.real && echo kept` prints `kept`; clean up both files afterwards.
- Depends on: T43, G03, G06, T10a. Size M.
- Notes: 'under 30 s' is an Inference from component timings.

### G09 oracle_dump.py: JSON test vectors for the iOS port
- Problem (Verified): decisions.md items 5-6 make an on-board iOS app the target with Python as the oracle; no Swift here; no task produces the vectors. Measured: walk_10s N=1000, true 18, counted 18, 36 hops WALKING; run_10s 27/28, 36 RUNNING; mixed_30s 63/64, 136 hops; 472 KB total; 6-decimal round trip reproduces count and states exactly.
- Change: oracle_dump.py (<= 45 lines); `os.environ.setdefault('STEPS_MODEL', '')` before importing steps. For walk_10s, run_10s, mixed_30s (`[('walk',10),('run',10),('walk',10)]`), seed 0: g, v, h, down; per hop `end in range(3*FS, len(acc)+1, 20)` feat and `classify_rule` state (ImportError fallback to classify); `count, states = count_steps(acc)`. Write `oracle/<name>.json` with fs, acc (6 decimals), true_steps, g, vertical, horizontal, hops (end + 7 features + state), count, states, generator ({'seed': 0, 'seq': seq, 'synth_sha256': sha256 of synth.py}). `--check` re-reads and asserts count and states, printing `ok <name>`. Docstring: regenerate when steps.py/orientation.py change.
- Acceptance: `cd /home/user/qmind-step-detector && python3 oracle_dump.py && python3 -c "import json; d=json.load(open('oracle/walk_10s.json')); print(len(d['acc']), d['true_steps'], d['count'], len(d['hops']), d['hops'][0]['state'])" && python3 -c "import json; d=json.load(open('oracle/mixed_30s.json')); print(d['true_steps'], d['count'], len(d['states']))" && python3 oracle_dump.py --check` -> prints `1000 18 18 36 WALKING`, `63 64 136`, then `ok walk_10s`, `ok run_10s`, `ok mixed_30s`. `du -sk oracle | cut -f1` prints a number below 1024.
- Depends on: T08, T01. Size M.
- Notes: counts measured on the unmodified steps.py; regenerate after T28/T31 (Inference that counts hold). The Swift track itself has no tasks here (see risks).

### G10 Team records the README section 2 set and runs ./check.sh data (needs_human)
- Problem (Verified): data/ is empty; goals 2 and 3 are measured on synthetic data only; T44 records a single walk; train.py's leave-one-out loops need >= 2 placements and >= 2 people.
- Change: Human: >= 2 people each record the five README section 2 recordings at 100 Hz with Accelerometer, Gravity, Gyroscope; export CSV; unzip into data/<name>_<walk|run|still>_<hand|pocket>/; steps.txt bare integer (0 for still); commit. Agent: `./check.sh data`; fix PROBLEM lines (rename, or human re-records); paste into README section 7 the `classifier:` and `overall:` lines from `STEPS_MODEL= python3 evaluate.py --data data`, the `label accuracy:` line, and the Leave-one-placement-out block of `python3 train.py data`, dated. Commit model.joblib only if the team decides to.
- Acceptance: `cd /home/user/qmind-step-detector && ls data | grep -cE '_(walk|run|still)_(hand|pocket)$'` prints at least `10`; `./check.sh data; echo exit=$?` ends with `CHECK OK` and `exit=0`; `python3 evaluate.py --data data | grep -E '^(overall|label accuracy)'` prints an `overall: true=<T> counted=<C> err=<e>%  <k>/<n> recordings within 3%` line and a `label accuracy:` line; `grep -c 'overall: true=' README.md` prints at least `1`.
- Depends on: G08, T44, G05 (README serialisation). Size S. needs_human=true.
- Notes: record in wave 0, same session as T44 and G05's cellular check; a failing check.sh line is the input to the next planning round.

## 5. Goal chains

1. Classify still/walking/running: T01 -> T02 -> T07 -> T32 -> T33 -> T34 -> T35 -> T37 -> T38 -> G06 -> G07; rule guarded by T04 -> T28 -> T28b (with T11) and T39.
2. Count steps within 3%: T01 -> T08 -> (T02, T07) -> T09 -> T10a -> T10b -> T15; counter fixes T28 -> T31; live path T12 -> T16 -> T17 -> T18; offline robustness T33 -> G02, G01; real data T44 -> G10.
3. A/B/C generalisation: T01 -> T02 -> T07 -> T33 -> T34 -> T35 -> T36, documented by T40 -> T41.
4. Live demo and pitch: T12 -> T31 -> T16 -> T17 -> T18 -> T24 -> T25b -> T26 -> T27 -> G05 -> G07 (server); T19; T20 -> T21 -> G04 (simulator); T29 -> T29b (spectrogram); T40 -> T41 -> T42 -> T43 -> T44 -> G05 -> G10 (README); G08 one-command gate; G09 oracle for the iOS port.

## 6. When real recordings arrive

1. `python3 check_recording.py data/*` (G03): fix every PROBLEM line by renaming or re-recording before anything else.
2. `python3 gyro_check.py data/<name>_walk_hand` (T44): confirms gyro units, sign and the measured rate; if the -gyro sign wins, negate the gyro in T24's `_gravity` and re-run T24's acceptance.
3. `STEPS_MODEL= python3 evaluate.py --data data` (T09/T10b) and `python3 evaluate.py --data data --live` (T15): the rule-based 3% gate and label accuracy; if a still recording counts 1-2 steps, decide a still tolerance (open question 8).
4. `python3 thresholds_report.py data` (T39) and `python3 ablation.py data` (T36): retune classify_rule's 0.4 / 2.35 / 5 and check which features are placement fingerprints.
5. `python3 train.py` (no argument: trains on data/ and saves model.joblib, T37); read the A/B/C/D per-fold tables (T34/T35) and update README 'What this shows' (T41) with the real result.
6. `./check.sh data` (G08) and paste its lines into README section 7 (G10).
7. `python3 oracle_dump.py` (G09) after any threshold change, so the Swift port tracks the final maths.

## 7. Known risks and open questions

1. Dependency check: T26 -> T25 and T43 -> T10 referenced split tasks; fixed to T25b and T10a+T10b. No cycle.
2. File conflicts between parallel tasks were serialised by adding depends_on (listed at the top of section 3): steps.py T08 -> T28 -> T31 -> T38 -> G06; train.py T07 -> T32 -> T33 -> T34 -> T35 -> T37 -> G02; evaluate.py T09 -> T10b -> T15 -> G06; server.py T12 -> T31 -> T16 -> T17 -> T18 -> T24 -> T25b -> T26 -> T27 -> G05 -> G07 (T19 edits only `__main__`); README T40 -> T41 -> T42 -> T43 -> T44 -> G05 -> G10; .gitignore T02 -> T29 -> T43 -> G08 (append-only, T43 greps first). Any agent whose branch conflicts on merge must rebase, not widen.
3. T10b's `label= 30%` / `93.4%` flip to 100% both after T28 and whenever model.joblib exists (Verified). Until G06 lands, run T10b's acceptance with no model.joblib in the repo root; after G06 use `STEPS_MODEL=`.
4. T43's original text said the --hard recordings fail the 3% gate: measured false (26/26 ok, +0.8%); the spec above removes that sentence.
5. The user's superseding decision (on-board iOS app, TestFlight, Mac with Xcode, no Apple Watch; decisions.md items 5-6) has no tasks: Swift package, N=200 direct DFT matching numpy bins, CMMotionManager raw-accelerometer spike, foreground-only limitation, TestFlight build all need their own wave with device-owned acceptance. G09 supplies the oracle vectors. Confirm with the user whether the on-board app replaces or complements the server demo on the day.
6. Real-data goals gate on two needs_human tasks (T44, G10). Schedule the phone session during wave 0; only the scripts and README edits wait for the chain.
7. T24 x T22 (Inference, traced): a deg/s stream with median < 20 rad/s but a flick > 35 rad/s would raise inside _analyse(); T24's spec now wraps gravity_complementary in try/except ValueError and falls back to the lowpass with source 'lowpass (gyro rejected)'.
8. evaluate.py's still rule (ok iff count == 0) fails the whole run if a real 20 s still recording counts one fidget step; decide a tolerance once G10's data exists.
9. Every expected number inherits numpy 2.4.6 RNG/QR conventions; teammates on numpy 1.x may see different fixture numbers. Pin `numpy>=2,<3` in requirements.txt (no task does; can be folded into T37's requirements.txt edit) or expect check.sh to fail for unrelated reasons.
10. matplotlib is not installed: T29's PNG branch is Unverified and the pitch has no static spectrogram figure; either add matplotlib to requirements.txt or render spectrogram.csv with the plotly already loaded by dashboard.html:2. Not planned.
11. Unverified on real phones: 100 Hz delivery (T17/G02 measure it), gyro units/sign (T44), arm-swing amplitude vs G_MIN=5.0 (T25a), whether iOS exports contain TotalAcceleration.csv or only Accelerometer+Gravity (train.load handles both), the cloudflared tunnel (G05).
12. Identifier assumptions across tasks (Inference until the earlier task lands): T12's `_count_locked`/`_analyse` (used by T24, T25b, T26, T31), T37's `--save` and `n_windows` (G06, G07, G08), T38's `load_model`/`MODEL_PATH`/`_model` (G06), T25a's `G_MIN/G_MAX` and T32's `parse_name` (G03), T21's `true steps: N` line (G04). Implementers read the landed code and adapt names; expected numbers do not change.
13. T15's claim that the live count equals the offline count for every recording is an Inference; its acceptance gates on the 3% band only.
14. T08's acceptance numbers in T09/T10b/G01/G02/G09 hold only if count_steps is implemented exactly as specified (hop 20 samples, warm-up 300, 4 s detection window, dedup 25/20 samples).

## 8. Appendix: dropped during verification

- T10: split into T10a (make_fixtures.py --hard) and T10b (evaluate.py label column); each half has its own acceptance and T10b needs T10a's dave folders. All numbers re-verified; the post-T28 'label >= 90%' Inference was tested and upgraded to Verified at 100%.
- T25: split into T25a (orientation.py: gravity_ok + norm floor) and T25b (server.py + dashboard.html: early return, no counting, error on the dashboard). As written it touched three files once the dashboard line was mandatory, and leaving it optional left the user-facing half unfixed.
- T30 (mean-subtraction DC-offset guard): the failure is real only for injected offsets; no source in this pipeline produces one (vertical = along - |g| uses the same lowpassed g for both terms; measured window means -0.002 to 0.007 m/s^2 across walk, swing, re-orientation and bias cases). The change had a verified cost: 1.4 Hz walk 92 -> 97 (true 83) and T31's slow-walk gate (<= 95) fails at 96. Re-open only after T24 with a measured offset from the complementary filter on real gyro data.
