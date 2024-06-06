import argparse
import re

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that compares the methods compiled between two client vlogs"
    )

    parser.add_argument('-c1', '--client_vlog_1', required=True)
    parser.add_argument('-c2', '--client_vlog_2', required=True)

    args = vars(parser.parse_args())

    client_vlog_1 = args['client_vlog_1']
    client_vlog_2 = args['client_vlog_2']

    file1_set = set()
    file2_set = set()
    with open(client_vlog_1) as file:
        for line in file:
            stuff = re.search("^[^@]*@", line)
            if stuff is not None:
                stuff = re.sub("\+ \(warm\)|\+ \(cold\)|\+ \(scorching\)|\+ \(hot\)", "", stuff.group())
                file1_set.add(stuff)
    with open(client_vlog_2) as file:
        for line in file:
            stuff = re.search("^[^@]*@", line)
            if stuff is not None:
                stuff = re.sub("\+ \(warm\)|\+ \(cold\)|\+ \(scorching\)|\+ \(hot\)", "", stuff.group())
                file2_set.add(stuff)
    diff1 = file1_set.difference(file2_set)
    diff2 = file2_set.difference(file1_set)
    print("difference between file1, file2: ")
    for line in diff1:
        print("file1 only: ", line)
    print("--------------------------------------------------------------------------------------------------")
    print("difference between file2, file1: ")
    for line in diff2:
        print("file2 only: ", line)

