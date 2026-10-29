import can, time, threading, csv, signal

IFACE = "vcan0"
OWNED_ID = 0x123
PERIOD = 0.010

stop = threading.Event()
signal.signal(signal.SIGINT, lambda *a: stop.set())
bus = can.Bus(interface="socketcan", channel=IFACE)


def legit_sender():
    seq = 0
    next_t = time.perf_counter()
    while not stop.is_set():
        data = [seq & 0xFF, 0, 0, 0, 0, 0, 0, 0]
        bus.send(can.Message(arbitration_id=OWNED_ID, data=data,
                             is_extended_id=False))
        seq += 1
        next_t += PERIOD
        time.sleep(max(0, next_t - time.perf_counter()))


def parrot_monitor():
    log = []
    while not stop.is_set():
        msg = bus.recv(timeout=0.2)
        if msg is None:
            continue
        if msg.arbitration_id == OWNED_ID:
            log.append((msg.timestamp, time.time(), msg.data.hex()))
            print(f"[SPOOF DETECTED] id=0x{msg.arbitration_id:X} data={msg.data.hex()}")
    with open("defender_log.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rx_kernel_ts", "detect_ts", "data_hex"])
        w.writerows(log)


t1 = threading.Thread(target=legit_sender)
t2 = threading.Thread(target=parrot_monitor)
t1.start(); t2.start()
t1.join(); t2.join()
bus.shutdown()
print("defender stopped, log written")