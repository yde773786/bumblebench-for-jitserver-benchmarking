import matplotlib.pyplot as plt
import sys
file = sys.argv[1]
s_list = []
s_time = []
s_count = 0
f_list = []
f_count = 0
f_time = []
oos_list = []
oos_count = 0
oos_time = []
is_failed = False
is_oos = False
is_success = False
# Read file line by line
with open(file) as f:
    for line in f:
        if 'notifying out-of-sequence thread' in line:
            is_oos = True
        if 'failed' in line:
            f_count += 1
            f_list.append(f_count)
            is_failed = True
            if is_oos:
                oos_count += 1
                oos_list.append(oos_count)
        if 'success' in line:
            s_count += 1
            s_list.append(s_count)
            is_success = True
        if 'elapsed' in line:
            if is_failed:
                f_time.append(float(line.split(':')[4]))
                is_failed = False
                if is_oos:
                    oos_time.append(float(line.split(':')[4]))
                    is_oos = False
            if is_success:
                s_time.append(float(line.split(':')[4]))
                is_success = False
# Plot the data
plt.plot(f_time, f_list, label='Failed')
plt.plot(s_time, s_list, label='Success')
plt.plot(oos_time, oos_list, label='Out of sequence')
plt.ylabel('Compilation Requests')
plt.xlabel('Time elapsed')
plt.legend()
plt.show()