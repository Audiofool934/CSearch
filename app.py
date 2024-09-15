import os
from flask import Flask, render_template, request, jsonify
from main import backend_main
from bs4 import BeautifulSoup
from tokenizer import segment_text

app = Flask(__name__)
saved_folder = ""

def get_results_from_folders(folder_list, saved_folder, query):
    results = []
    for folder, url in folder_list:

        index_html_path = os.path.join(folder, "index.html")
        with open(index_html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title = soup.title.string if soup.title else "No Title"

        index_content_path = os.path.join(folder, "index_content.txt")
        with open(index_content_path, "r", encoding="utf-8") as f:
            content_preview = f.read()

        query_words = segment_text(query, "stopwords-master").split("/")

        title = highlight_words(title, query_words)
        highlighted_content = highlight_words(content_preview, query_words)

        result = {
            "url": url,
            "title": title,
            # 'folders': folders,
            "description": highlighted_content,
        }
        results.append(result)
    return results


def highlight_words(text, words):
    """
    高亮显示文本中的指定词语，使用 <span> 标签。
    """
    for word in words:
        if word:
            text = text.replace(word, f'<span class="highlight">{word}</span>')
    return text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    
    data = request.json
    query = data.get('query', '')
    domains = set(data.get('domains', []))
    saved_folder = "saved"

    results = backend_main(
        target_urls=domains,
        target_domains=domains,
        root=saved_folder,
        stopwords_dir="stopwords-master",
        query=query,
        top_k=60,
    )

    results = get_results_from_folders(results, saved_folder, query)
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12345, debug=True)
