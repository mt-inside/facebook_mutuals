#!/usr/bin/env python

token = ""

import logging
import sys
import requests

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(fmt)
log.addHandler(sh)

def get_mutuals(id):
    log.info("Getting mutuals for " + id)
    r = requests.get(
        "https://graph.facebook.com/v2.7/{}".format(id),
        params = {
            "fields": "context.fields(mutual_friends)",
            "access_token": token
        }
    )

    return r.json()["context"]["mutual_friends"]["summary"]["total_count"]

def get_friends(id):

    # Rather than this recusrion, should either foldl() or iterate with a yield
    # (kinda pointless becuase we need all of them to sort)
    def get_friends_page(id, after):
        log.info("Getting friends after " + after)
        r = requests.get(
            "https://graph.facebook.com/v2.7/{}/friends".format(id),
            params = {
                "limit": 2,
                "after": after,
                "access_token": token
            }
        )

        page = r.json()["data"]
        log.info(page)

        ms = map(lambda f: { "friend": f, "mutuals": get_mutuals(f["id"]) }, page)

        if ("next" in r.json()["paging"]):
            return ms + get_friends_page(id, r.json()["paging"]["cursors"]["after"])
        else:
            return ms


    fs = get_friends_page(id, "")
    return fs

def main(args=None):
    if token == "":
        sys.exit("Please provide an access token")

    fs = get_friends("me")
    sfs = sorted(fs, key = lambda f: f["mutuals"], reverse=True)

    for f in sfs:
        print(f["friend"]["name"] + ": " + str(f["mutuals"]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
