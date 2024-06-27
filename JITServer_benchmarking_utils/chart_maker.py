import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that takes in a configuration of kernels and uses BumbleBench for JITServer to benchmark"
    )

    parser.add_argument('-d', '--data_cdf_hist', required=True)
    parser.add_argument('-v', '--vlog_gantt', required=True)
    parser.add_argument('-f', '--figure_export_name', required=False)
    parser.add_argument('-clw', '--continuous_load_wrapper', action='store_true')


    args = vars(parser.parse_args())

    data_cdf_hist = args['data_cdf_hist']
    vlog_gantt = args['vlog_gantt']
    figure_export_name = args['figure_export_name']
    continuous_load_wrapper = args['continuous_load_wrapper']

    cmd = f'python3 cdf_grapher.py -d {data_cdf_hist} -f cdf_chart_maker'
    if continuous_load_wrapper is True:
        cmd = cmd + " -clw"
    proc = subprocess.Popen(cmd, shell=True)

    cmd = f'python3 cdf_grapher.py -d {data_cdf_hist} -f histogram_chart_maker -his'
    if continuous_load_wrapper is True:
        cmd = cmd + " -clw"
    proc = subprocess.Popen(cmd, shell=True)

    cmd = f'python3 gantt_chart.py -d {vlog_gantt}'
    proc = subprocess.Popen(cmd, shell=True)
