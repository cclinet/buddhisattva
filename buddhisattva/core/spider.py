import re
import time
from math import ceil
import os
from pathlib import Path

import httpx
from loguru import logger

custom_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/108.0.0.0 Safari/537.36"
}

img_base_pattern = re.compile(r'"_ATTACH_BASE_VIEW":"(.*?)"')
rows_pattern = re.compile(r'"__ROWS":(\d+)')
rows_per_page_pattern = re.compile(r'"__R__ROWS_PAGE":(\d+)')
sub_urls_pattern = re.compile(r'"attachurl":"(.*?)"')
subject_pattern = re.compile(r'"subject":"(.*?)"')


def save_img(img_base_url, sub_urls, base_path):
    for sub_url in sub_urls:
        url = f"https://{img_base_url}/{sub_url}"
        r = httpx.get(url, headers=custom_headers)
        img_name = sub_url.split("/")[-1]
        img_path = f"{base_path}/{img_name}"
        with open(img_path, "wb") as f:
            f.write(r.content)


def parse_header(headers, guestJs, ngaPassportUid=None):
    header_parse = headers["set-cookie"].split(";")
    header_parse = [i.strip() for i in header_parse]
    cookies = {"guestJs": str(guestJs)}
    if ngaPassportUid:
        cookies["ngaPassportUid"] = ngaPassportUid
    for header in header_parse:
        if header.startswith("lastvisit"):
            k, v, *_ = header.split("=")
            cookies["lastvisit"] = v
        elif (not ngaPassportUid) and header.startswith("secure, ngaPassportUid"):
            k, v, *_ = header.split("=")
            cookies["ngaPassportUid"] = v
    return cookies


def spider(
    tid: int | str | None,
    save_dir=None,
    nga_url: str = "https://bbs.nga.cn/read.php",
    web_ui=False,
):
    tmp_res = httpx.get(f"{nga_url}?tid={tid}", headers=custom_headers)
    if save_dir is None:
        if web_ui:
            logger.error("save_dir can not be None if env is web_ui")
        save_dir = Path(__file__).parents[2] / "content"
    logger.debug("base dir is {}", save_dir)

    first_request_time: int = int(time.time())
    cookies = parse_header(tmp_res.headers, first_request_time)
    time.sleep(3)

    page = 1
    subject = None
    path = None

    while True:
        logger.debug(f"page: {page}")
        res = httpx.get(
            f"{nga_url}?tid={tid}&page={page}&lite=js",
            cookies=cookies,
            headers=custom_headers,
        )
        if res.status_code != 200:
            logger.error("http code is {},可能是帖子被隐藏，或者 cookie 设置失败", res.status_code)
            break
        d = res.text
        img_base = re.findall(img_base_pattern, d)[0]
        rows = int(re.findall(rows_pattern, d)[0])
        rows_per_page = int(re.findall(rows_per_page_pattern, d)[0])
        sub_urls = re.findall(sub_urls_pattern, d)
        subject = subject or re.findall(subject_pattern, d)[0]
        path = path or save_dir / subject
        if page == 1:
            os.makedirs(path, exist_ok=True)

        save_img(img_base, sub_urls, path)

        total_page = ceil(rows / rows_per_page)
        if page >= total_page:
            break
        else:
            page += 1
            cookies = parse_header(
                res.headers, cookies["guestJs"], cookies["ngaPassportUid"]
            )
            time.sleep(1)
