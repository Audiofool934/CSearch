import math
import os
from ii_tc import build_term_counts
from utils import load_dict_json, save_list_json, save_test_results, bonus
from tokenizer import segment_text, extract_text, segment_query

def compute_query_tf_idf(
    inverted_index: dict, query_segs: str, query_tc: dict, total_documents: int
) -> dict:
    """计算query的tf-idf

    Args:
        inverted_index (dict): 总的倒排索引
        query_segs (str): query的分词
        query_tc (dict): query的词频字典
        total_documents (int): 总文档书，用来计算idf

    Returns:
        dict: query的tf-idf
    """
    query_idf = {}
    query_segs = query_segs.split("/")  # 假设词是以“/”分隔的
    for term in query_segs:
        if term in inverted_index:
            query_idf[term] = math.log(
                total_documents / (1 + len(inverted_index[term]))
            )
        else:
            query_idf[term] = 0

    return {
        term: (1 + math.log(query_tc.get(term, 0))) * idf
        for term, idf in query_idf.items()
    }
    

def cosine_similarity(tf_idf: dict, query_tf_idf: dict) -> float:
    """计算两个（不等长）字典向量的余弦相似度

    Args:
        tf_idf (dict): doc的tf-idf
        query_tf_idf (dict): query的tf-idf

    Returns:
        float: doc和query的余弦相似度
    """
    all_terms = set(tf_idf.keys()).union(set(query_tf_idf.keys()))

    tf_idf = {term: tf_idf.get(term, 0) for term in all_terms}
    query_tf_idf = {term: query_tf_idf.get(term, 0) for term in all_terms}

    dot_product = sum(tf_idf[key] * query_tf_idf[key] for key in tf_idf)

    magnitude1 = math.sqrt(sum(value**2 for value in tf_idf.values()))
    magnitude2 = math.sqrt(sum(value**2 for value in query_tf_idf.values()))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    else:
        return dot_product / (magnitude1 * magnitude2)


def top_k_similarity(tf_idf_dict: dict, query_tf_idf: dict, top_k: int) -> list:
    """计算每个文档与查询的余弦相似度

    Args:
        tf_idf_dict (dict): 所有文档的tf-idf
        query_tf_idf (dict): query的tf-idf

    Returns:
        list: 每个文档与查询的余弦相似度
    """
    similarities = []
    for doc, _ in tf_idf_dict.items():
        similarity = cosine_similarity(tf_idf_dict[doc]["tf_idf"], query_tf_idf)
        similarities.append((doc, similarity))

    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    top_k = sorted_similarities[:top_k]
    return [doc_id for doc_id, _ in top_k]


def query_request(
    query: str, stopwords_dir: str, dict_path: str, root: str, top_k: int, tf_idf_dict: dict, inverted_index: dict
) -> list[tuple]:
    """query请求pipeline

    Args:
        query (str): 待查询query
        stopwords_dir (str): 停用词目录
        inverted_index (dict): 倒排索引
        tf_idf_dict (dict): 所有文档的tf-idf
    """

    query_segs = segment_query(query, stopwords_dir)
    query_tc = build_term_counts(query_segs, query)

    total_documents = len(tf_idf_dict)

    query_tf_idf = compute_query_tf_idf(
        inverted_index, query_segs, query_tc, total_documents
    )

    top_k_docs = top_k_similarity(tf_idf_dict, query_tf_idf, top_k)

    return top_k_docs, query_segs

def calculate_score(text: str, query:str, query_segs: list) -> int:
        """计算文本的匹配得分

        Args:
            text (str): 从结果中提取的文本
            query_segs (list): 查询字符串分词结果

        Returns:
            int: 匹配得分
        """
        score = 0
        for seg in query_segs:
            count = text.count(seg)
            
            if bonus(text, seg, "#", 7):
                score += pow(len(seg), 3) * count
                continue
            
            score += pow(len(seg), 2) * count

        if bonus(text, query, "#", 7):
            score += pow(len(query), 5) * text.count(query)
        else:
            score += pow(len(query), 4) * text.count(query)
    
        return score


def query_booster(results:list, query:str, query_segs:str)->list:
    """基于字符串匹配的检索结果增强模块

    Args:
        results (list): 检索结果（URL/文档路径）
        query (str): 查询字符串
        query_segs (list): 查询字符串分词结果
    """

    if isinstance(query_segs, str):
        query_segs = query_segs.split("/")
            
    query_segs = sorted(query_segs, key=len)
    if query_segs[-1] == query:
        query_segs.pop()
    
    scored_results = []
    for doc in results:
        doc_file = os.path.join(doc, "index_content.txt")
        with open(doc_file, 'r', encoding='utf-8') as file:
            text = file.read()
        score = calculate_score(text, query, query_segs)
        scored_results.append((doc, score))
        
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    filtered_results = []
    
    for result in scored_results:
        if len(filtered_results) > 20:
            break
        if "index" in result[0]:
            continue
        filtered_results.append(result)
    
    # save_test_results(query, query_segs, [(os.path.relpath(result[0], "saved").replace("_", "://", 1), result[1]) for result in filtered_results])
    
    return [result[0] for result in filtered_results]