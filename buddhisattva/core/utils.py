import os

import httpx

custom_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}


def save_img(subject, img_base, urls):
    base_dir = subject
    os.makedirs(f"content/{base_dir}", exist_ok=True)
    for sub in urls:
        url = f"https://{img_base}/{sub}"
        r = httpx.get(url, headers=custom_headers)
        img_name = sub.split("/")[-1]
        img_path = f"content/{base_dir}/{img_name}"
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
