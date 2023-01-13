import json
import time
from math import ceil

import httpx

from utils import custom_headers, parse_header, save_img

# Set tid here
tid = 34974372


tmp_res = httpx.get(f"https://bbs.nga.cn/read.php?tid={tid}", headers=custom_headers)
first_request_time: int = int(time.time())

cookies = parse_header(tmp_res.headers, first_request_time)
time.sleep(3)
page = 1
while True:
    res = httpx.get(
        f"https://bbs.nga.cn/read.php?tid={tid}&page={page}&lite=js",
        cookies=cookies,
        headers=custom_headers,
    )
    data = json.loads(res.text[len("window.script_muti_get_var_store=") :])["data"]

    img_base = data["__GLOBAL"]["_ATTACH_BASE_VIEW"]
    reply = data["__R"]
    post = data["__T"]
    rows = data["__ROWS"]
    rows_per_page = data["__R__ROWS_PAGE"]

    reply_contains_img = []
    for _, d in reply.items():
        if d.get("attachs") is not None:
            reply_contains_img.append(d)

    save_img(post["subject"], img_base, reply_contains_img)

    total_page = ceil(rows / rows_per_page)
    if page >= total_page:
        break
    else:
        print(cookies)
        page += 1
        cookies = parse_header(
            res.headers, cookies["guestJs"], cookies["ngaPassportUid"]
        )
        time.sleep(1)
