import os
import math
from collections import defaultdict
from utils import save_dict_json, load_dict_json

def build_tf_idf(inverted_index: dict, term_counts: dict) -> dict:
    """基于倒排索引和词频表构建TF-IDF

    Args:
        inverted_index (dict): 已构建好的倒排索引
        term_counts (dict): 已构建好的词频表

    Returns:
        dict: 更新后的词频表（现在包含了idf和tf-idf）
    """
    total_documents = len(term_counts)

    for doc, term in term_counts.items():
        term_counts[doc]["idf"] = {}
        term_counts[doc]["tf_idf"] = {}

        for term2, tc in term["tc"].items():
            term_counts[doc]["idf"][term2] = math.log(
                total_documents / (1 + len(inverted_index[term2]))
            )
            term_counts[doc]["tf_idf"][term2] = (1 + math.log(tc)) * term_counts[doc]["idf"][term2]

    return term_counts


def combine_tf_idf(
    tc_list: list[dict], ii_list: list[dict], tf_idf_save_path: str
) -> dict:
    """合并多个域名的TF-IDF

    Args:
        tc_list (list[dict]): 多个域名的词频表
        ii_list (list[dict]): 多个域名的倒排索引

    Returns:
        dict: 合并后的TF-IDF
    """
    # 合并倒排索引
    combined_inverted_index = defaultdict(set)
    for ii in ii_list:
        for term, docs in ii.items():
            combined_inverted_index[term].update(docs)

    total_documents = sum(len(tc) for tc in tc_list)

    tf_idf = defaultdict(lambda: defaultdict(dict))
    for tc in tc_list:
        for doc, term in tc.items():
            for term2, tc2 in term["tc"].items():
                idf = math.log(
                    total_documents / (1 + len(combined_inverted_index[term2]))
                )
                tf = math.log(1 + tc2)
                tf_idf[doc]["tf_idf"][term2] = tf * idf

    combined_ii_save_path = os.path.join(tf_idf_save_path, "combined_ii.json")
    tf_idf_save_path = os.path.join(tf_idf_save_path, "tf_idf.json")

    save_dict_json(combined_inverted_index, combined_ii_save_path)
    save_dict_json(tf_idf, tf_idf_save_path)


def tf_idf_build_and_save(save_path):

    term_counts = load_dict_json(os.path.join(save_path, "term_counts.json"))
    inverted_index = load_dict_json(os.path.join(save_path, "inverted_index.json"))
    tf_idf = build_tf_idf(inverted_index, term_counts)
    save_dict_json(tf_idf, os.path.join(save_path, "tf_idf.json"))