import os
import subprocess
from datetime import datetime

def get_file_commit_date(filepath):
    try:
        cmd = ['git', 'log', '-1', '--format=%cI', filepath]
        result = subprocess.check_output(cmd).decode('utf-8').strip()
        return datetime.fromisoformat(result)
    except Exception as e:
        print(f"Could not get commit date for {filepath}: {e}")
        return datetime.min

html_files = []
for root, _, files in os.walk('.'):
    if '.git' in root or '.github' in root:
        continue
    for file in files:
        if file.endswith('.html') and file != 'index.html':
            filepath = os.path.join(root, file)
            html_files.append({
                'path': filepath.lstrip('./'),
                'date': get_file_commit_date(filepath)
            })

html_files.sort(key=lambda x: x['date'], reverse=True)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html lang="zh-CN">\n')
    f.write('<head>\n')
    f.write('    <meta charset="UTF-8">\n')
    f.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    f.write('    <title>网站目录</title>\n')
    f.write('    <script src="https://cdn.tailwindcss.com"><\/script>\n')
    f.write('    <style>\n')
    f.write("        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }\n")
    f.write('    </style>\n')
    f.write('</head>\n')
    f.write('<body class="bg-slate-50 text-slate-800">\n')
    f.write('    <div class="container mx-auto max-w-3xl p-4 md:p-8">\n')
    f.write('        <header class="text-center mb-10">\n')
    f.write('            <h1 class="text-3xl md:text-4xl font-bold text-slate-900">网站内容索引</h1>\n')
    f.write('            <p class="mt-2 text-slate-600">所有页面均按最后更新时间倒序排列。</p>\n')
    f.write('        </header>\n')
    f.write('        <div class="mb-8">\n')
    f.write('            <input type="text" id="searchInput" placeholder="在此输入关键词进行搜索..." class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition">\n')
    f.write('        </div>\n')
    f.write('        <main>\n')
    f.write('            <div id="fileList" class="space-y-4">\n')
    
    if not html_files:
        f.write('<p class="text-center text-slate-500">暂无内容。</p>\n')
    else:
        f.write('<ul class="space-y-3">\n')
        for item in html_files:
            date_str = item['date'].strftime('%Y-%m-%d')
            list_item = f"""                <li class="file-item bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300">\n                    <a href="{item['path']}" class="flex justify-between items-center">\n                        <span class="file-name text-lg font-medium text-sky-700 hover:text-sky-600">{item['path']}</span>\n                        <span class="text-sm text-slate-500">{date_str}</span>\n                    </a>\n                </li>\n"""
            f.write(list_item)
        f.write('</ul>\n')
    
    f.write('            </div>\n')
    f.write('        </main>\n')
    f.write('        <footer class="text-center mt-12 py-4 border-t">\n')
    f.write('            <p class="text-sm text-slate-500">索引由 GitHub Actions 自动生成</p>\n')
    f.write('        </footer>\n')
    f.write('    </div>\n')
    f.write('    <script>\n')
    f.write("        const searchInput = document.getElementById('searchInput');\n")
    f.write("        const fileList = document.getElementById('fileList');\n")
    f.write("        const items = fileList.getElementsByClassName('file-item');\n")
    f.write("        searchInput.addEventListener('input', function(e) {\n")
    f.write("            const searchTerm = e.target.value.toLowerCase();\n")
    f.write("            for (let i = 0; i < items.length; i++) {\n")
    f.write("                const item = items[i];\n")
    f.write("                const fileName = item.querySelector('.file-name').textContent.toLowerCase();\n")
    f.write("                if (fileName.includes(searchTerm)) {\n")
    f.write("                    item.style.display = '';\n")
    f.write("                } else {\n")
    f.write("                    item.style.display = 'none';\n")
    f.write("                }\n")
    f.write("            }\n")
    f.write("        });\n")
    f.write('    <\/script>\n')
    f.write('</body>\n')
    f.write('</html>\n')

print("Index page generated successfully.")

