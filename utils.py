import os
import re
import json
from collections import deque
from urllib.parse import urlparse
import logging
import pickle
import dill

# ------------------------------ for crawler.py ------------------------------ #


def url_to_path(url: str, save_path: str) -> str:
    """把url转换为保存路径

    Args:
        url (str): 输入的url
        save_path (str): root保存路径

    Returns:
        str: 保存路径
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    host_name = parsed_url.hostname
    path = parsed_url.path.rstrip("/")
    save_path = os.path.join(save_path, f"{scheme}_{host_name}", path)
    os.makedirs(save_path, exist_ok=True)
    return save_path


def configure_logging(save_path: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(save_path, "crawler.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def save_state(fp_links: set, queue: deque, save_path: str) -> None:
    with open(os.path.join(save_path, "crawler_state.pkl"), "wb") as f:
        pickle.dump((list(fp_links), list(queue)), f)


def load_state(save_path: str) -> tuple:
    try:
        with open(os.path.join(save_path, "crawler_state.pkl"), "rb") as f:
            fp_links, queue = pickle.load(f)
            return set(fp_links), deque(queue)
    except FileNotFoundError:
        return set(), deque()


# ------------------------------- for ii_tf.py ------------------------------- #


# Save inverted index to a file using JSON
def save_dict_json(data, file_path):
    """保存字典到JSON文件，处理set类型"""

    def convert_sets_to_lists(obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: convert_sets_to_lists(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_sets_to_lists(elem) for elem in obj]
        else:
            return obj

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(convert_sets_to_lists(data), json_file, ensure_ascii=False, indent=4)


def load_dict_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_segmented_and_content(index_segmented_path, index_content_path):
    with open(index_segmented_path, "r", encoding="utf-8") as f:
        index_segmented = f.read().strip().split("/")

    with open(index_content_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    return index_segmented, index_content


# ------------------------------- for query.py ------------------------------- #


def save_list_json(file_path, data_list):
    with open(file_path, "w") as f:
        json.dump(data_list, f, indent=4)


def save_dill(file_path, data):
    with open(file_path, "wb") as f:
        dill.dump(data, f)
        
def load_dill(file_path):
    with open(file_path, "rb") as f:
        return dill.load(f)
    
def save_test_results(query, query_segs, scored_results, output_file='query_results.json'):
    """将查询结果保存到 JSON 文件中

    Args:
        query (str): 查询字符串
        query_segs (list): 查询字符串分词结果
        scored_results (list): 评分后的检索结果
        output_file (str): JSON 文件名，默认是 'query_results.json'
    """
    
    query_results_dict = {
        "query": query,
        "segs": query_segs,
        "results": scored_results
    }
    
    output_file = 'query_results.json'

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.append(query_results_dict)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
    
def bonus(main_str, sub_str, target, radius):
    sub_str_indices = [i for i in range(len(main_str)) if main_str.startswith(sub_str, i)]
    target_pattern = re.compile(rf'(?<!{re.escape(target)}){re.escape(target)}(?!{re.escape(target)})')
    
    for index in sub_str_indices:
        start = max(0, index - radius)
        end = min(len(main_str), index + len(sub_str) + radius)
        surrounding_text = main_str[start:end]
        if target_pattern.search(surrounding_text):
            return True
    
    return False


