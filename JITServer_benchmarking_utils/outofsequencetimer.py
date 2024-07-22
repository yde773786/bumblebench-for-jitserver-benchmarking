import sys

file = open(sys.argv[1], 'r')
print(sys.argv[1])

is_oos = False
oos_counter = 0
count = 0
count2 = 0

for line in file:

    if 'out-of-sequence' in line:
        is_oos = True


    if "Elapsed Time processing entry from client " in line:
        t = line.split("<")
        b = t[2].split(">")[0]
        count += float(b)

        if is_oos:
            oos_counter += 1
            count2 += float(b)
            is_oos = False
            if (float(b) < 1):
                print(line)
                exit(0)

print(count)
print(f'oos: {count2}')
print(oos_counter)