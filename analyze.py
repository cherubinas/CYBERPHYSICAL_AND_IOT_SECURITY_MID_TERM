import csv, statistics as st

att = {r["data_hex"]: float(r["send_ts"]) for r in csv.DictReader(open("attacker_log.csv"))}
det = list(csv.DictReader(open("defender_log.csv")))

detected, false_pos, lat = set(), 0, []
for r in det:
    key = r["data_hex"]
    if key in att:
        detected.add(key)
        lat.append((float(r["rx_kernel_ts"]) - att[key]) * 1000)  # ms
    else:
        false_pos += 1

lat.sort()
print(f"attack frames sent : {len(att)}")
print(f"detected           : {len(detected)}  (detection rate {len(detected)/len(att):.1%})")
print(f"missed             : {len(att) - len(detected)}")
print(f"false positives    : {false_pos}")
if lat:
    print(f"latency ms  mean={st.mean(lat):.3f}  median={st.median(lat):.3f}  "
          f"p95={lat[int(0.95*len(lat))-1]:.3f}  max={lat[-1]:.3f}")