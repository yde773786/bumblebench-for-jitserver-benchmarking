import sys
# data/baseline_dotty_50stag_vlog : 2055048
# data/aldcf_dotty_50stag_vlog : 1841412
# data/ldcf_dotty_50stag_vlog : 1700220
# data/baseline_future_10stag_vlog : 343888
# data/aldcf_future_10stag_vlog : 351152
# data/ldcf_future_10stag_vlog : 384948
# data/baseline_mix_30stag_vlog : 1412232
# data/aldcf_mix_30stag_vlog : 1498008
# data/ldcf_mix_30stag_vlog : 1418920


#SUCCESSFUL COMPILATIONS
# data/baseline_dotty_50stag_vlog : 511324
# data/aldcf_dotty_50stag_vlog : 455920
# data/ldcf_dotty_50stag_vlog : 392418
# data/baseline_future_10stag_vlog : 83976
# data/aldcf_future_10stag_vlog : 81780
# data/ldcf_future_10stag_vlog : 77996
# data/baseline_mix_30stag_vlog : 351171
# data/aldcf_mix_30stag_vlog : 370439
# data/ldcf_mix_30stag_vlog : 339463
if __name__ == "__main__":
    files = ["data/baseline_dotty_50stag_vlog", "data/aldcf_dotty_50stag_vlog", "data/ldcf_dotty_50stag_vlog",
             "data/baseline_future_10stag_vlog", "data/aldcf_future_10stag_vlog", "data/ldcf_future_10stag_vlog",
             "data/baseline_mix_30stag_vlog", "data/aldcf_mix_30stag_vlog", "data/ldcf_mix_30stag_vlog"]
    for file in files:
        INPUT = open(file, 'r')

        counter = 0
        # read line by line
        for line in INPUT:
            if 'has successfully compiled' in line:
                counter += 1

        print(f'{file} : {counter}')
