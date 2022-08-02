import sys
times = []
thresh = sys.argv[2]
with open(sys.argv[1], "r") as f:
    for line in f:
        info = line.split()
        split = info[1]
        hms = split.split(":")
        split_len = float(hms[0]) * 3600 + float(hms[1]) * 60 + float(hms[2])
        if split_len < float(thresh):
            continue
        hms = info[2].split(":")
        len = float(hms[0]) * 3600 + float(hms[1]) * 60 + float(hms[2])
        times.append(len)

with open(sys.argv[1], "w") as f:
    for time in times:
        f.write(f"{time}\n")
    f.close()
