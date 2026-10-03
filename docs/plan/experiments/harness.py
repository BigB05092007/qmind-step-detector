"""Offline harness: replay simulate.py-style signals through server.state()
without HTTP, polling every 200 ms like dashboard.html does."""
import sys, importlib, numpy as np
sys.path.insert(0, "/home/user/qmind-step-detector")
FS = 100

def make(mode_seq, seed=0, stride_asym=0.0, swing_deg=0.0):
    """mode_seq: list of (mode, seconds). stride_asym: extra spike amp on every
    other step (pocket leg asymmetry). swing_deg: phone rotates +-swing_deg about
    a horizontal axis at stride frequency (arm swing)."""
    rng = np.random.default_rng(seed)
    R, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    phase, true, out = 0.0, 0, []
    for mode, secs in mode_seq:
        for _ in range(int(secs * FS)):
            if mode == "still":
                world = np.array([0, 0, 9.81]) + rng.normal(0, 0.05, 3)
            else:
                f, amp = (1.8, 3.0) if mode == "walk" else (2.8, 9.0)
                old = phase; phase += f / FS
                if int(phase) > int(old): true += 1
                s = phase % 1
                a = amp * (1 + stride_asym * (int(phase) % 2))
                vert = a * np.exp(-((s - 0.1) / 0.06) ** 2) - a * 0.15
                world = np.array([0.6*np.sin(np.pi*phase), 0.3*np.sin(2*np.pi*phase), 9.81 + vert])
                world += rng.normal(0, 0.25, 3)
            th = np.radians(swing_deg) * np.sin(np.pi * phase)   # stride-rate swing
            Rs = np.array([[1,0,0],[0,np.cos(th),-np.sin(th)],[0,np.sin(th),np.cos(th)]])
            out.append(R.T @ Rs @ world)
    return np.array(out), true

def run_live(acc, poll_s=0.2):
    import server; importlib.reload(server)
    states, cads = [], []
    step = int(poll_s * FS)
    for i in range(0, len(acc), step):
        server.ingest([{"name": "totalacceleration", "values": dict(zip("xyz", v))} for v in acc[i:i+step]])
        s = server.state()
        if s["ready"]: states.append(s["state"]); cads.append(s["cadence"])
    return server.steps["count"], states, cads

if __name__ == "__main__":
    from collections import Counter
    cases = {
        "walk 60s":                [("walk", 60)],
        "run 60s":                 [("run", 60)],
        "walk30 run30 walk30":     [("walk", 30), ("run", 30), ("walk", 30)],
        "still 20s":               [("still", 20)],
    }
    for name, seq in cases.items():
        for kw in [{}, {"stride_asym": 0.5}, {"swing_deg": 30}]:
            acc, true = make(seq, **kw)
            n, st, cad = run_live(acc)
            err = (n - true) / true * 100 if true else float("nan")
            print(f"{name:22s} {str(kw):22s} true={true:4d} counted={n:4d} err={err:+6.1f}%  "
                  f"states={dict(Counter(st))}  cadences={sorted(set(np.round(cad,2)))}")
    # dashboard throttled: poll every 5 s instead of 200 ms
    acc, true = make([("walk", 60)])
    n, *_ = run_live(acc, poll_s=5.0)
    print(f"walk 60s, polled every 5 s: true={true} counted={n}")
