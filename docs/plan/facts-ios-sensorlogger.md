# Verified facts for the iOS wave and the demo wave (from the scout agent + local probes)

Sources: Apple developer docs (JSON endpoints), github.com/tszheichoi/awesome-sensor-logger (README, UNITS, PUSHING, COORDINATES, CROSSPLATFORM), local probes. Status labels as given by the scout; "Local" = run in this session.

## Sensor Logger push payload (PUSHING.md) — VERIFIED
- POST application/json: `{ messageId, sessionId, deviceId, userId?, payload: [ { name, time, values: {z, y, x}, accuracy? } ] }`
- `time` is UTC epoch nanoseconds, per sample. Messages can arrive out of order (`messageId` exists for that).
- XYZ stream names in the official schema: magnetometeruncalibrated, gyroscopeuncalibrated, accelerometeruncalibrated, magnetometer, gyroscope, accelerometer, gravity. `totalacceleration` is NOT in the published schema (Android-only, undocumented; server.py accepts it anyway).
- Server should return 200. Returning 499 with a text body shows that text to the user in the app once per recording (useful for "wrong streams enabled" feedback).
- Consequence: `deviceId`/`sessionId` are available -> per-device keying in server.py is possible (server.py:12-15 currently has one global buffer and one counter).

## Sensor Logger on iOS — VERIFIED
- iOS logs Accelerometer.csv (gravity REMOVED) + Gravity.csv; TotalAcceleration.csv is Android-only. train.py:28-31 and server.py:27-28 already combine them.
- Units: m/s^2, g = 9.80665. (The `< 3 -> *9.81` heuristic in server.py:39 and train.py:34 is for the uncalibrated/g-unit case.)
- CSV header is exactly `time,seconds_elapsed,z,y,x` (z before x). train.py reads by column name, so fine. Author: read by header name, never by position.
- Metadata.csv has: platform (ios/android), appVersion, device id, sensors, sampleRateMs (10 = 100 Hz), standardisation (true/false).
- "Standardise Units & Frames" flips the sign of all three axes on iOS to match Android. Local check (algebra on orientation.py:35-42): a global sign flip leaves `vertical` and `horizontal` unchanged (down flips with g), so step counting is unaffected; only the displayed `down` vector flips and tilt uses abs(down[2]).
- Sampling is approximate and never perfectly even (author's warning). iOS exports observed at ~10 ms spacing. Use `time`/`seconds_elapsed`, not an assumed 100 Hz, for anything precise.

## Local probe: iOS ingest path on synthetic data — Local, VERIFIED
- scratchpad/ios_probe.py: accelerometer (gravity removed) + gravity as separate streams, 1 s packets, three orderings (interleaved / gravity-first / accel-first), walk & run, with and without 30 deg arm swing: counts within +/-1% and all windows classified correctly. Stale "last-seen gravity" pairing (server.py:25-28) is at most a 1% effect here. Pairing by timestamp is hardening, not a bug fix.
- Note: simulate.py only ever sends `totalacceleration`; add an iOS-style mode so the demo path the team will actually use is exercised.

## CoreMotion (for the iOS port) — VERIFIED unless marked
- Raw total acceleration (gravity included): `CMMotionManager.startAccelerometerUpdates(to:withHandler:)` -> `CMAccelerometerData.acceleration` (CMAcceleration). Units: G (1.0 = 9.8 m/s^2). Multiply by 9.80665 to match the Python pipeline.
- Fused outputs to AVOID for the orientation step: `CMDeviceMotion.gravity`, `.userAcceleration` (total = gravity + userAcceleration). Using them means CoreMotion solved "find down", not the team's code.
- Rate: `accelerometerUpdateInterval = 0.01` -> 100 Hz "usually at least 100 Hz" (Apple); CMMotionManager caps at 100 Hz (WWDC23). Check `CMAccelerometerData.timestamp` (seconds since boot) for the true interval. Developer report: 40 Hz and 100 Hz honoured exactly on iPhone, 60/80 Hz rounded.
- Create exactly one CMMotionManager; check `isAccelerometerAvailable`; do not deliver to the main queue; call stopAccelerometerUpdates().
- `NSMotionUsageDescription` is NOT required for CMMotionManager (required for CMSensorRecorder, CMPedometer, CMMotionActivityManager).
- BACKGROUND LIMITATION (important for "phone in pocket, screen locked"): there is no UIBackgroundModes value for motion. A suspended app cannot be woken by accelerometer input (Apple DTS). Developer reports: updates stop on backgrounding unless the app keeps running under another background mode (audio/location), which is a policy grey area, and even then need stop/restart on transition. `CMSensorRecorder` records at 50 Hz for up to 12 h while suspended but is batch (readable later), not real-time, and only on some models (A10+ reported). => A fully independent iOS app can do LIVE counting only with the screen on / app foregrounded, or via batch (CMSensorRecorder at 50 Hz, which changes FS and the FFT bin spacing).

## Swift on Linux (for agent-run tests) — VERIFIED unless marked
- `swift test` runs XCTest on Linux; Ubuntu is a supported platform; Docker one-liner `docker run -v "$PWD:/code" -w /code swift:latest swift test`. Swift Testing also supported on Linux (Swift 6).
- No toolchain in this container (`swift: command not found`, Ubuntu 24.04 x86_64). A prerequisite task "install Swift toolchain" is needed, subject to the environment's network policy.
- Accelerate/vDSP is Apple-platforms only (no Linux). The port needs its own FFT. For a 2 s window at 100 Hz, N = 200: a direct DFT (O(N^2) = 40k complex mults per window) is trivial and matches numpy's rfft bins exactly; zero-padding to 256 would change bin spacing and break the oracle comparison. Keep an optional `#if canImport(Accelerate)` fast path (UNVERIFIED quote; SE-0075 pattern).
- Avoid `import simd` in the Linux-testable package (UNVERIFIED availability); stdlib SIMD3<Double> is fine.

## Axis conventions — VERIFIED
- Device frame: x = screen horizontal, y = screen vertical, z = out of screen; axes stick to the device. iOS and Android differ by a sign on all three axes (face-up on a table: gravity -z on iOS, +z on Android). Apple diagrams show inertial force (opposite of applied force).
- As above, orientation.py is invariant to a global sign flip, so the port does not need to care for counting; it does for displaying "down".
