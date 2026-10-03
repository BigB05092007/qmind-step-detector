# Decisions made with the user (to fold into the task plan)

1. Architecture stays "collect on phone, process elsewhere" (Sensor Logger -> server.py / train.py). On-phone processing is NOT replacing it.
2. iOS app: add as a FINAL wave, gated on the Python pipeline hitting the 3% step-count target on real recordings.
   - Port only orientation.py + steps.py maths to Swift.
   - Must read raw accelerometer (CMMotionManager.accelerometerData), never CMDeviceMotion.gravity / userAcceleration.
   - Python output on identical input is the test oracle.
   - No Swift toolchain in this container (Verified: `swift: command not found`, Ubuntu 24.04 x86_64). iOS tasks need either a "install Swift for Linux" prerequisite task or needs_human=true at the acceptance step.
3. Public-URL demo task (user said yes): in the demo wave, add "run server.py behind a public URL (tunnel such as ngrok / Cloudflare Tunnel, or a small persistent host; NOT serverless because server.py:12-15 holds buffer and counter in process memory) and verify a phone can stream to it from cellular".
   - Prerequisites: counting moved off the GET /state poll (server.py:67-69); consider per-device keying since server.py:12-15 is a single global buffer/counter (whether Sensor Logger's payload carries a device id is pending the scout agent).
   - needs_human=true for the final phone-from-cellular check; the tunnel setup and a curl-based smoke test can be done by an agent.
4. Team is all-iPhone. The repo already handles iOS's accelerometer+gravity split (server.py:27-28, train.py:28-31).

## SUPERSEDES decision 2 (user, later in the conversation): "The team wants a fully on board iOS app I think"
5. Target product is now a fully on-board iOS app that detects and counts LIVE on the phone. The Python pipeline remains the reference implementation and the test oracle; train.py / the A/B/C experiment stay on the laptop.
   - The iOS track is no longer "last wave, optional": it becomes a parallel track that starts as soon as the maths is stable enough to port, with a spike first to prove the background-sampling mechanism (see facts-ios-sensorlogger.md: no background mode for motion; keep-alive workarounds under research in workflow wf_71684d86-46f).
   - Still gated: do not freeze thresholds in Swift until the Python pipeline hits 3% on real recordings; keep the oracle test so Swift tracks Python.
   - The hard constraint stands: raw CMMotionManager accelerometer into the team's own orientation code. CMPedometer / CMDeviceMotion only as comparison.
   - The public-URL server demo (decision 3) stays as the fallback demo path in case the on-board mechanism fails on the day.
   - Phrase "I think" noted: confirm with the user before any task assumes App Store distribution vs. internal/TestFlight builds, since that changes which keep-alive mechanisms are acceptable.
6. Answered by the user:
   - Distribution: Internal / TestFlight only. No App Store review -> App Review Guideline 2.5.4 does not gate the choice of keep-alive mechanism; pick whatever is most reliable. Still prefer a mechanism with a legitimate framing so a later App Store path is not closed.
   - Hardware: a Mac with Xcode; a PAID Apple Developer account (TestFlight available; device installs do not expire after 7 days). NO Apple Watch -> the watch workout-session route is out of scope; drop or mark as "not available" in the plan.
7. Answered by the user after the workflows ran: "On board app replaces everything". The iOS app is the only demo path; server.py / dashboard.html / simulate.py are legacy tooling, their 18 tasks are dropped (docs/plan/README.md §0). The Python pipeline stays as reference implementation, trainer (train.py, A/B/C) and oracle for the Swift port. User also asked to push everything: plan documents committed under docs/plan/.
