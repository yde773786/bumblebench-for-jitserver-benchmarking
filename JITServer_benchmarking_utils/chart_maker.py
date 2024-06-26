import argparse
import os
import datetime as Date
import random
import subprocess
from pathlib import Path

import config_comparer
from jitserver_benchmarker import main_function

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that takes in a configuration of kernels and uses BumbleBench for JITServer to benchmark"
    )

    parser.add_argument('-d1', '--data_cdf_hist', required=True)
    parser.add_argument('-d2', '--data_gantt', required=True)
    parser.add_argument('-f', '--figure_export_name', required=False)
    parser.add_argument('-clw', '--continuous_load_wrapper', action='store_true')


    args = vars(parser.parse_args())

    data_cdf_hist = args['data_cdf_hist']
    data_gantt = args['data_gantt']
    figure_export_name = args['figure_export_name']
    continuous_load_wrapper = args['continuous_load_wrapper']
