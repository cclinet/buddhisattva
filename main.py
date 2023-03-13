import re
import time
from math import ceil

import httpx

from utils import custom_headers, parse_header, save_img


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tid", help="tid from url", nargs="?", default=None)
args = parser.parse_args()


# Set tid here
tid = None or args.tid

if tid is None:
    print("ERROR!,必须设置pid")
    exit()

img_base_pattern = re.compile(r'"_ATTACH_BASE_VIEW":"(.*?)"')
rows_pattern = re.compile(r'"__ROWS":(\d+)')
rows_per_page_pattern = re.compile(r'"__R__ROWS_PAGE":(\d+)')
sub_urls_pattern = re.compile(r'"attachurl":"(.*?)"')
subject_pattern = re.compile(r'"subject":"(.*?)"')

tmp_res = httpx.get(f"https://bbs.nga.cn/read.php?tid={tid}", headers=custom_headers)
first_request_time: int = int(time.time())

cookies = parse_header(tmp_res.headers, first_request_time)
time.sleep(3)
page = 1
subject = None
while True:
    print(f"page: {page}")
    res = httpx.get(
        f"https://bbs.nga.cn/read.php?tid={tid}&page={page}&lite=js",
        cookies=cookies,
        headers=custom_headers,
    )
    if res.status_code != 200:
        print(f"ERROR!http code is {res.status_code},可能是帖子被隐藏，或者 cookie 设置失败")
        break
    d = res.text
    img_base = re.findall(img_base_pattern, d)[0]
    rows = int(re.findall(rows_pattern, d)[0])
    rows_per_page = int(re.findall(rows_per_page_pattern, d)[0])
    sub_urls = re.findall(sub_urls_pattern, d)
    subject = subject or re.findall(subject_pattern, d)[0]

    save_img(subject, img_base, sub_urls)

    total_page = ceil(rows / rows_per_page)
    if page >= total_page:
        break
    else:
        # print(cookies)
        page += 1
        cookies = parse_header(
            res.headers, cookies["guestJs"], cookies["ngaPassportUid"]
        )
        time.sleep(1)
