import os
from slugify import slugify

from crawler import links_scraper_bfs_parallel
from tokenizer import token4search
from ii_tc import ii_tc_build_and_save
from tf_idf import tf_idf_build_and_save, combine_tf_idf
from query import query_request, query_booster

from utils import url_to_path, load_dict_json
from build import (
    check_build_status,
    update_build_status,
    reset_build_status,
)
from history import load_history, update_history


def build_one_domain(url: str, domain: str, root: str, stopwords_dir: str) -> None:
    """build一个域名下的所有信息

    Args:
        url (str): 爬虫起点url
        domain (str): 想要的域名
        root (str): 保存地址根目录
        stopwords_dir (str): 停用词目录
        query (str): 查询字符串
    """
    save_path = url_to_path(url=domain, save_path=root)

    # ----------------------------------- crawl ---------------------------------- #

    links_scraper_bfs_parallel(
        url=url, domain=domain, save_path=save_path, max_depth=32, max_workers=6
    )

    # --------------------------------- tokenize --------------------------------- #

    # init_build_status(root, domain, "tokenize")
    if check_build_status(root, domain, "tokenize"):
        token4search(stopwords_dir, save_path)
        update_build_status(root, domain, "tokenize")

    # ----------------------------------- ii-tc ---------------------------------- #

    # init_build_status(root, domain, "ii-tc")
    if check_build_status(root, domain, "ii-tc"):
        ii_tc_build_and_save(save_path)
        update_build_status(root, domain, "ii-tc")

    # ---------------------------------- tf-idf ---------------------------------- #
    
    # init_build_status(root, domain, "tf-idf")
    if check_build_status(root, domain, "tf-idf"):
        tf_idf_build_and_save(save_path)
        update_build_status(root, domain, "tf-idf")
        

def build_domains(
    target_urls: set[str],
    target_domains: set[str],
    root: str,
    dict_path: str,
    stopwords_dir: str,
) -> None:

    for domain in target_domains:
        build_one_domain(
            url=domain, domain=domain, root=root, stopwords_dir=stopwords_dir
        )

    tc_list = []
    ii_list = []

    for domain in target_domains:
        tc_list.append(
            load_dict_json(os.path.join(url_to_path(domain, root), "term_counts.json"))
        )
        ii_list.append(
            load_dict_json(
                os.path.join(url_to_path(domain, root), "inverted_index.json")
            )
        )

    combine_tf_idf(tc_list, ii_list, tf_idf_save_path=dict_path)


def backend_main(
    target_urls: set[str],
    target_domains: set[str],
    root: str,
    stopwords_dir: str,
    query: str,
    top_k: int,
) -> list[str]:
    domains_key = slugify(str(sorted(target_domains)))
    history_path = os.path.join(root, "history")
    history_file_path = os.path.join(history_path, "history.json")

    skip = True
    if domains_key in load_history(history_file_path):
        skip = False
        
    history = update_history(history_path, target_domains)
    dict_path = history[domains_key]["dict_path"]
    
    if skip:
        build_domains(target_urls, target_domains, root, dict_path, stopwords_dir)
    
    tf_idf = load_dict_json(os.path.join(dict_path, "tf_idf.json"))
    combined_ii = load_dict_json(os.path.join(dict_path, "combined_ii.json"))
    
    top_k_docs, query_segs = query_request(
        query=query,
        stopwords_dir=stopwords_dir,
        dict_path=dict_path,
        root=root,
        top_k=top_k,
        tf_idf_dict=tf_idf,
        inverted_index=combined_ii,
    )

    top_k_docs = query_booster(top_k_docs, query, query_segs)
    
    top_k_docs = [
        (doc, os.path.relpath(doc, root).replace("_", "://", 1)) for doc in top_k_docs
    ]
    
    return top_k_docs


def main(
    target_urls: set[str],
    target_domains: set[str],
    root: str,
    stopwords_dir: str,
    query: str,
    top_k: int,
    tf_idf,
    combined_ii,
) -> None:
    
    domains_key = slugify(str(sorted(target_domains)))
    history_path = os.path.join(root, "history")
    history_file_path = os.path.join(history_path, "history.json")

    skip = True
    if domains_key in load_history(history_file_path).keys():
        skip = False

    history = update_history(history_path, target_domains)
    dict_path = history[domains_key]["dict_path"]

    if skip:
        build_domains(target_urls, target_domains, root, dict_path, stopwords_dir)
        tf_idf = load_dict_json(os.path.join(dict_path, "tf_idf.json"))
        combined_ii = load_dict_json(os.path.join(dict_path, "combined_ii.json"))
    
    top_k_docs, query_segs = query_request(
        query=query,
        stopwords_dir=stopwords_dir,
        dict_path=dict_path,
        root=root,
        top_k=top_k,
        tf_idf_dict=tf_idf,
        inverted_index=combined_ii,
    )

    top_k_docs = query_booster(top_k_docs, query, query_segs)
    
    top_k_docs = [
        os.path.relpath(doc, root).replace("_", "://", 1) for doc in top_k_docs
    ]
    
    return top_k_docs


if __name__ == "__main__":

    target_urls: set[str] = {
        "https://gsai.ruc.edu.cn",
        "http://ai.ruc.edu.cn",
        "https://www.jiqizhixin.com",
    }

    target_domains: set[str] = {
        "https://gsai.ruc.edu.cn",
        "http://ai.ruc.edu.cn",
        "https://www.jiqizhixin.com",
    }

    root: str = "saved"

    stopwords_dir = "stopwords-master"

    query = "情感分析在各个维度和方面取得了显著的发展。该领域已从传统的粗粒度分析（如文档和句子级别分析）发展到细粒度分析"

    tf_idf = None
    combined_ii = None

    top_k_docs = main(
        target_urls=target_urls,
        target_domains=target_domains,
        root=root,
        stopwords_dir=stopwords_dir,
        query=query,
        top_k=60,
        
        tf_idf=tf_idf,
        combined_ii=combined_ii,
    )

    for doc in top_k_docs:
        print(doc)