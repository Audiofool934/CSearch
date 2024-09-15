import os
from collections import defaultdict
from utils import save_dict_json, read_segmented_and_content


def build_term_counts(index_segmented: str, index_content: str) -> dict:
    """计算制定文档的tf(s)，如果index_segmented是str，则转为list，否则直接使用（这里认为index_segmented一定是分词表）

    Args:
        index_segmented (str): 分词表
        index_content (str): 待统计内容

    Returns:
        dict: 分词后的term-frequency字典
    """
    if isinstance(index_segmented, str):
        index_segmented = index_segmented.split("/")

    term_count = {}
    for term in index_segmented:
        term_count[term] = index_content.count(term)

    return term_count


def build_ii_tc(save_path: str) -> tuple:
    """构建倒排索引(inverted_index)和词频表(term_counts)

    Args:
        save_path (str): 目标根目录

    Returns:
        tuple: inverted_index, term_counts
    """
    inverted_index = defaultdict(set)
    term_counts = {}

    for root, _, files in os.walk(save_path):
        for file in files:
            document_id = root

            index_segmented_path = os.path.join(root, "index_segmented.txt")
            index_content_path = os.path.join(root, "index_content.txt")

            if not os.path.exists(index_segmented_path) or not os.path.exists:
                continue

            index_segmented, index_content = read_segmented_and_content(
                index_segmented_path, index_content_path
            )

            for term in index_segmented:
                inverted_index[term].add(document_id)

            tc = build_term_counts(index_segmented, index_content)

            term_counts[document_id] = {}
            term_counts[document_id]["tc"] = tc

    return inverted_index, term_counts


def ii_tc_build_and_save(save_path: str) -> None:
    """构建并保存ii_tc

    Args:
        save_path (str): 目标根目录
    """

    inverted_index, term_counts = build_ii_tc(save_path)

    inverted_index_path = os.path.join(save_path, "inverted_index.json")
    save_dict_json(inverted_index, inverted_index_path)
    term_counts_path = os.path.join(save_path, "term_counts.json")
    save_dict_json(term_counts, term_counts_path)