// script.js
document.getElementById('add-query').addEventListener('click', addDomainField);

function addDomainField() {
    const domainContainer = document.getElementById('domain-container');
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'search-domain';
    input.placeholder = 'Domain';
    
    domainContainer.appendChild(input); // 在“加号”按钮之前插入新输入框
}

function performSearch() {
    const domains = [];
    const domainInputs = document.getElementsByName('search-domain');
    domainInputs.forEach(input => {
        if (input.value.trim() !== '') {
            domains.push(input.value.trim());
        }
    });

    const query = document.getElementById('search-query').value.trim();  // 获取唯一查询输入框的值

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query, domains: domains }),  // 发送查询和域名数组
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';  // 清空之前的结果

        data.forEach(result => {
            const resultCard = document.createElement('div');
            resultCard.className = 'result-card';

            const resultTitle = document.createElement('a');
            resultTitle.className = 'result-title';
            resultTitle.href = result.url;  // 生成超链接
            resultTitle.innerHTML = result.title || '无标题';

            const resultDescriptionCard = document.createElement('div');
            resultDescriptionCard.className = 'result-description-card';

            const resultDescription = document.createElement('div');
            resultDescription.className = 'result-description';
            resultDescription.innerHTML = result.description || '无描述';

            resultDescriptionCard.appendChild(resultDescription);
            resultCard.appendChild(resultTitle);
            resultCard.appendChild(resultDescriptionCard);
            resultsDiv.appendChild(resultCard);
        });
    });
}