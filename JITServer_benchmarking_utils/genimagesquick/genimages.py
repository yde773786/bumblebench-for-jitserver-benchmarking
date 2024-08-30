import subprocess

if __name__ == "__main__":
    cmds = ["python3 ../ttl_runtime_helper.py -i ../work0816/dotty50.csv -s1 per_client_cdf_dotty -n 50 -p 80",
            "python3 ../ttl_runtime_helper.py -i ../work0816/future_genetic.csv -s1 per_client_cdf_future -n 50 -p 80",
            "python3 ../temperature_histogram.py ../work0816/baseline_vlog_dotty_50 baseline_dotty_temp",
            "python3 ../temperature_histogram.py ../work0816/baseline_vlog_future_genetic baseline_future_temp",
            "python3 ../create_infra_warmup_graphs.py",
            "python3 ../compilation_distribution.py -d ../work0816/baseline_vlog_dotty_50 -his  -f "
            "compilation_distribution_dotty"]

    for cmd in cmds:
        proc = subprocess.Popen(cmd, shell=True)