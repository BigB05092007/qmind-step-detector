"""Does server.ingest's iOS path (accelerometer + gravity as separate streams,
gravity paired by 'last seen') count correctly? simulate.py and harness.py only
ever exercised the Android-style 'totalacceleration' path."""
import sys, importlib, numpy as np
sys.path.insert(0, "/home/user/qmind-step-detector")
from harness import make, FS
from orientation import gravity_lowpass
from collections import Counter

def run(acc, layout, pkt_s=1.0, poll_s=0.2):
    import server; importlib.reload(server)
    g = gravity_lowpass(acc)              # stand-in for CoreMotion's fused gravity
    user = acc - g                        # stand-in for Sensor Logger 'accelerometer' (gravity removed)
    n = int(pkt_s * FS); step = int(poll_s * FS); states = []
    for i in range(0, len(acc), n):
        a_s = [{"name": "accelerometer", "values": dict(zip("xyz", v))} for v in user[i:i+n]]
        g_s = [{"name": "gravity", "values": dict(zip("xyz", v))} for v in g[i:i+n]]
        if layout == "accel_then_gravity": payload = a_s + g_s
        elif layout == "gravity_then_accel": payload = g_s + a_s
        else: payload = [x for pair in zip(g_s, a_s) for x in pair]   # interleaved
        server.ingest(payload)
        # the dashboard polls several times per packet-second
        for _ in range(max(1, n // step)):
            s = server.state()
            if s["ready"]: states.append(s["state"])
    return server.steps["count"], dict(Counter(states))

for kw in [{}, {"swing_deg": 30}]:
    for seq in [[("walk", 60)], [("run", 60)]]:
        acc, true = make(seq, **kw)
        print(f"{seq[0][0]:4s} {str(kw):18s} true={true}", end="  ")
        for layout in ["interleaved", "gravity_then_accel", "accel_then_gravity"]:
            n, st = run(acc, layout)
            print(f"| {layout}: {n} ({(n-true)/true*100:+.0f}%) {st}", end=" ")
        print()
