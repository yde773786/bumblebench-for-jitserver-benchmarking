# python3 verifier_round_robin.py <path_to_file> 

import sys

log = open(sys.argv[1], 'r').readlines()
output = open('recent0627/output.txt', 'w')

first_cql = first_crql = False

for line in log:
    if '#INFO:  CQL' in line:
        if first_cql == False:
            first_cql = True
            output.write('Client Queue Log:\n')
            output.write('[' + line.split()[2] + ', ')
        else:
            output.write(line.split()[2] + ', ')
    elif '#INFO:  CRQL' in line:

        if first_cql:
            output.write(']\n')
            first_cql = False

        if first_crql == False:
            first_crql = True
            output.write('Compilation Request Queue Log:\n')
            output.write(f"[ {line.split()[2].split(',')[0]} ({line.split()[3]}), ")
        else:
            output.write(f"{line.split()[2].split(',')[0]} ({line.split()[3]}),")

    elif '#INFO:  NMTBC' in line:
        if first_crql:
            output.write(']\n')
            first_crql = False
        output.write(f'Next Method to be Compiled: {line.split()[2]}\n')
    else:
        if first_cql:
            output.write(']\n')
            first_cql = False
        elif first_crql:
            output.write(']\n')
            first_crql = False
