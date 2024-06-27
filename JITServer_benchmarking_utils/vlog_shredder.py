import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that makes a vlog much smaller"
    )
    parser.add_argument('-d', '--data', required=True)
    args = vars(parser.parse_args())
    total_data = args['data']
    start_time = 0
    client_set = set()
    file2 = open(total_data+'_condensed', "w+")
    print(f'opening {total_data}_condensed')
    with open(total_data, "r") as file:
        for row in file:
            if "#INFO:  Elapsed Time processing entry from client" in row:
                file2.write(row)
    file2.close()
    print("done")
    exit(0)