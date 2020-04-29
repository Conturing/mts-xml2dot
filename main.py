import logging
import sys
import datetime as dt

from dot2xml import mts_to_dot, mc_to_dot
from parse_dot import parse_dot
from parse_xml import parse_xml
from test_case import read_directory

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
stdout_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler(f'log/{dt.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[stdout_handler, file_handler])
log = logging.getLogger('log')

if __name__ == "__main__":
    read_directory("examples/problem101-decomposition-DAG.dot")
