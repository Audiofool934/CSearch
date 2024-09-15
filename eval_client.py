import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, parent_dir)

import json
import requests
import getpass
from utils import load_dict_json
from urllib.parse import urljoin
from eval_search_engine import evaluate

# 待填充，助教在调试完成后会公布使用的base_url
base_url = "http://223.4.87.133:3389/"


def input_idx():
    idx = input("idx: ")
    # maybe some restrictions
    return idx


def input_passwd():
    passwd = getpass.getpass("passwd for final submission (None for debug mode): ")
    if passwd == "":
        print("=== DEBUG MODE ===")
    return passwd


def login(idx, passwd):
    url = urljoin(base_url, "login")
    r = requests.post(url, data={"idx": idx, "passwd": passwd})
    r_dct = eval(r.text)
    queries = r_dct["queries"]
    if r_dct["mode"] == "illegal":
        raise ValueError("illegal password!")
    print(f"{len(queries)} queries.")
    return queries


def send_ans(idx, passwd, urls):
    url = urljoin(base_url, "mrr")
    r = requests.post(
        url, data={"idx": idx, "passwd": passwd, "urls": json.dumps(urls)}
    )
    r_dct = eval(r.text)
    if r_dct["mode"] == "illegal":
        raise ValueError("illegal password!")
    return r_dct["mode"], r_dct["mrr"]

def main():
    idx = input_idx()
    passwd = input_passwd()
    queries = login(idx, passwd)
    # print(queries)

    tot_urls = []
    
    for index, query in enumerate(queries):
        print(f"finish {index}..\n")
        urls = evaluate(query)
        tot_urls.append(urls)

    mode, mrr = send_ans(idx, passwd, tot_urls)
    print(f"MRR@20: [{mrr}], [{mode}] mode")


if __name__ == "__main__":
    
    # main()
    
    tf_idf = load_dict_json("saved/history/http-ai-ruc-edu-cn-https-gsai-ruc-edu-cn-https-www-jiqizhixin-com/tf_idf.json")
    
    combined_ii = load_dict_json("saved/history/http-ai-ruc-edu-cn-https-gsai-ruc-edu-cn-https-www-jiqizhixin-com/combined_ii.json")
    
    idx = input_idx()
    passwd = input_passwd()
    queries = login(idx, passwd)
    print(queries)

    tot_urls = []
    
    for index, query in enumerate(queries):
        print(f"finish {index}..\n")
        urls = evaluate(query, tf_idf, combined_ii)
        tot_urls.append(urls)

    mode, mrr = send_ans(idx, passwd, tot_urls)
    print(f"MRR@20: [{mrr}], [{mode}] mode")