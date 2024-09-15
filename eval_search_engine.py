import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, parent_dir)

from main import main

def evaluate(query: str, tf_idf, combined_ii) -> list:
    """
    各位同学需要完成evaluate函数，通过调用之前自己的代码来实现搜索引擎的功能
    参数：query，字符串类型，它代表查询
    返回值：url_list，它是一个长为20的url列表
    """
    
    target_urls: set[str] = {
        "https://gsai.ruc.edu.cn",
        "http://ai.ruc.edu.cn",
        "https://www.jiqizhixin.co4m",
    }

    target_domains: set[str] = {
        "https://gsai.ruc.edu.cn",
        "http://ai.ruc.edu.cn",
        "https://www.jiqizhixin.com",
    }

    root: str = "saved"

    stopwords_dir = "stopwords-master"

    url_list = main(
        target_urls=target_urls,
        target_domains=target_domains,
        root=root,
        stopwords_dir=stopwords_dir,
        query=query,
        top_k=60,
        
        tf_idf=tf_idf,
        combined_ii=combined_ii,
    )
    
    return url_list