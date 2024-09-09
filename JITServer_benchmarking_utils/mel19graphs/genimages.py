import subprocess
# per_client_cdf_dotty: {'FCFS': [4252.079999999999], 'LDCF': [3613.417999999999], 'RR': [4497.164000000002], 'ALDCF': [3930.275999999999]}
# per_client_cdf_future: {'FCFS': [2226.1600000000003], 'LDCF': [2050.8119999999994], 'RR': [2335.748], 'ALDCF': [2130.7820000000006]}
# total_dotty : {'FCFS': 179289.90000000002, 'ALDCF': 163316.87999999998, 'RR': 190715.05, 'LDCF': 149277.28999999998}
# total_future : {'FCFS': 85645.12000000001, 'ALDCF': 85864.35, 'RR': 89299.17, 'LDCF': 101247.19999999997}
# per_client_cdf_mix_dotty : {'FCFS': [3247.864], 'LDCF': [3684.338000000001], 'RR': [3294.6480000000006], 'ALDCF': [3544.7919999999995]}
# per_client_cdf_mix_future : {'FCFS': [1127.3339999999996], 'LDCF': [635.2620000000001], 'RR': [1071.3039999999996], 'ALDCF': [737.9079999999997]}
# total_mix : {'FCFS': 94351.33, 'ALDCF': 91902.81000000003, 'RR': 94160.44, 'LDCF': 95554.02000000003}
if __name__ == "__main__":
    cmds = ["python3 ../ttl_runtime.py -i data/dotty50stag.csv -s1 per_client_dotty -s2 total_dotty -n 50",
            "python3 ../ttl_runtime.py -i data/future10stag.csv -s1 per_client_future -s2 total_future -n 50",
            "python3 ../ttl_runtime.py -i data/mix30stag.csv -s1 per_client_mix -s2 total_mix -n 50",
            "python3 ../ttl_runtime_helper.py -i data/dotty50stag.csv -s1 per_client_cdf_dotty -n 50 -p 80",
            "python3 ../ttl_runtime_helper.py -i data/future10stag.csv -s1 per_client_cdf_future -n 50 -p 80",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix -n 50 -p 80",
            "python3 ../ttl_runtime_helper.py -i data/dotty50stag.csv -s1 per_client_cdf_dotty_all -n 50 -lp",
            "python3 ../ttl_runtime_helper.py -i data/future10stag.csv -s1 per_client_cdf_future_all -n 50 -lp",
            "python3 ../ttl_runtime_helper.py -i data/dotty50stag.csv -s1 per_client_cdf_dotty_all_percentiles -n 50 -lp -vl -p 80",
            "python3 ../ttl_runtime_helper.py -i data/future10stag.csv -s1 per_client_cdf_future_all_percentiles -n 50 -lp -vl -p 80",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_all -n 50 -lp",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_future_all -n 50 -lp -mo",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_dotty_all -n 50 -lp -me",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_future_all_percentiles -n 50 -lp -mo -vl -p 80",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_dotty_all_percentiles -n 50 -lp -me -vl -p 80",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_future -n 50 -mo",
            "python3 ../ttl_runtime_helper.py -i data/mix30stag.csv -s1 per_client_cdf_mix_dotty -n 50 -me",
            "python3 ../temperature_histogram.py data/baseline_dotty_50stag_vlog baseline_dotty_temp",
            "python3 ../temperature_histogram.py data/baseline_future_10stag_vlog baseline_future_temp",
            "python3 ../temperature_histogram.py data/baseline_mix_30stag_vlog baseline_mix_temp",
            "python3 ../create_infra_warmup_graphs.py",
            "python3 ../compilation_distribution.py -d data/baseline_dotty_50stag_vlog -his  -f "
            "compilation_distribution_dotty",
            "python3 ../compilation_distribution.py -d data/baseline_future_10stag_vlog -his  -f "
            "compilation_distribution_future",
            "python3 ../create_cdf_graphs.py"]

    for cmd in cmds:
        proc = subprocess.Popen(cmd, shell=True)