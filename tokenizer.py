import os
from bs4 import BeautifulSoup
import jieba


def load_stopwords(stopwords_dir: str) -> set:
    """加载停用词

    Args:
        stopwords_dir (str): 停用词目录

    Returns:
        set: 停用词集合
    """
    stopwords = set()
    for filename in os.listdir(stopwords_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(stopwords_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                stopwords.update(line.strip() for line in f)
    return stopwords


def extract_text(file_path: str) -> str:
    """提取html文件中的文本内容

    Args:
        file_path (str): html文件路径

    Returns:
        str: 提取的文本内容
    """
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        content = []

        if soup.title:
            content.append(f"#{soup.title.string.strip()}")

        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
            text = element.get_text(strip=True)
            if element.name.startswith("h"):
                content.append(f"#{text}#")
            
            elif element.name == "p":
                paragraph_text = "".join(
                    child.get_text(strip=True)
                    for child in element.find_all(string=True)
                )
                if paragraph_text:
                    content.append(paragraph_text)

            elif element.name == "li":
                content.append(f"- {text}")

        full_text = "\n\n".join(content)
        return full_text


def segment_text(text: str, stopwords_dir: str) -> str:
    """使用jieba.cut_for_search分词，返回用"/"分割后的文本

    Args:
        text (str): 待分词文本
        stopwords_dir (str): 停用词目录

    Returns:
        str: 分词后的文本
    """

    stopwords = load_stopwords(stopwords_dir)

    words = jieba.cut_for_search(text)

    filtered_words = [word for word in words if word not in stopwords and word.strip()]

    segmented_text = "/".join(filtered_words)

    return segmented_text

def segment_query(text: str, stopwords_dir: str) -> str:

    stopwords = load_stopwords(stopwords_dir)
    words = jieba.cut(text, cut_all=False)

    filtered_words = [word for word in words if word not in stopwords and word.strip()]

    segmented_text = "/".join(filtered_words)

    return segmented_text


def token4search(stopwords_dir: str, save_path: str) -> None:
    """将整个目录下的html文件提取文本内容并分词，保存到同目录下的_content.txt和_segmented.txt文件中

    Args:
        stopwords_dir (str): 停用词目录
        save_path (str): 保存目标路径
    """

    if not os.path.exists(save_path):
        print("Error: domain save_path does not exist.")

    for root, _, files in os.walk(save_path):
        for file in files:
            if file.endswith(".html") or file.endswith(".htm"):
                file_path = os.path.join(root, file)

                text = extract_text(file_path)
                output_file_path = os.path.splitext(file_path)[0] + "_content.txt"
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(text)

                segmented_text = segment_text(text, stopwords_dir)

                segmented_output_path = (
                    os.path.splitext(file_path)[0] + "_segmented.txt"
                )

                with open(
                    segmented_output_path, "w", encoding="utf-8"
                ) as segmented_file:
                    segmented_file.write(segmented_text)