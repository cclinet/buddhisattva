import argparse
from buddhisattva.core.spider import spider

parser = argparse.ArgumentParser()
parser.add_argument("tid", help="tid from url", nargs="?", default=None)
args = parser.parse_args()

# Set tid here
tid = 35645216 or args.tid
spider(tid)
