# DOXUB Ultra-Fast Search Engine ( @solorblaze )

import mmap
import re
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

try:
    import pyrogram
    from pyrogram.methods.utilities.idle import idle
    import platform
    import datetime
    import os
except:
    print("Load modules", end="")
    import subprocess, time
    print(".", end="")
    subprocess.Popen(["pip", "install", "pyrogram", "--break-system-packages"])
    print("..")
    print("Modules loaded!")
    time.sleep(1)

if not os.path.exists("settings.doxub"):
    with open("settings.doxub", "w") as settings:
        api_id = int(input("Your api id: "))
        api_hash = input("Your api hash: ")
        settings.write(f"{api_id}\n{api_hash}")

with open("settings.doxub") as settings:
    lines = settings.readlines()
    api_id = int(lines[0])
    api_hash = lines[1]

MAX_WORKERS = multiprocessing.cpu_count() * 2
CHUNK_SIZE = 1024 * 1024 * 50

client = pyrogram.Client("client.doxub", api_id, api_hash)

def process_large_file(file_path, pattern):
    results = []
    keys = []
    separator = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line:
                non_word_chars = re.findall(r'[^\w]', first_line)
                separator = max(set(non_word_chars), key=non_word_chars.count) if non_word_chars else None
                keys = first_line.split(separator) if separator else [first_line]
        
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                chunk_start = 0
                pattern_bytes = pattern.encode('utf-8')
                
                while chunk_start < len(mm):
                    chunk_end = min(chunk_start + CHUNK_SIZE, len(mm))
                    chunk = mm[chunk_start:chunk_end]
                    
                    for match in re.finditer(pattern_bytes, chunk, flags=re.IGNORECASE):
                        match_start = match.start()
                        match_end = match.end()
                        context_start = max(match_start - 50, 0)
                        context_end = min(match_end + 50, len(chunk))
                        
                        try:
                            context = chunk[context_start:context_end].decode('utf-8', errors='replace')
                            if separator:
                                values = context.split(separator)
                                if len(values) == len(keys):
                                    results.append(values)
                                else:
                                    results.append(context.split('\t'))
                            else:
                                results.append(context.split('\t'))
                        except UnicodeDecodeError:
                            continue
                    
                    chunk_start = chunk_end
                    
    except Exception as e:
        print(f"Error processing large file {file_path}: {e}")
    if len(results) == 0:
        return None
    return {
        "title": os.path.basename(file_path),
        "columns": keys,
        "data": results
    }

def ultra_fast_search(file_path, pattern):
    results = []
    keys = []
    separator = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line:
                non_word_chars = re.findall(r'[^\w]', first_line)
                separator = max(set(non_word_chars), key=non_word_chars.count) if non_word_chars else None
                keys = first_line.split(separator) if separator else [first_line]
        
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                pattern_bytes = pattern.encode('utf-8')
                
                for match in re.finditer(pattern_bytes, mm, flags=re.IGNORECASE):
                    match_start = match.start()
                    match_end = match.end()
                    context_start = max(match_start - 50, 0)
                    context_end = min(match_end + 50, len(mm))
                    
                    try:
                        context = mm[context_start:context_end].decode('utf-8', errors='replace')
                        if separator:
                            values = context.split(separator)
                            if len(values) == len(keys):
                                results.append(values)
                            else:
                                results.append(context.split('\t'))
                        else:
                            results.append(context.split('\t'))
                    except UnicodeDecodeError:
                        continue
                        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    if len(results) == 0:
        return None
    return {
        "title": os.path.basename(file_path),
        "columns": keys,
        "data": results
    }

def generate_html_tables(tables: list[dict], search) -> str:
    def format_cell_text(text: str) -> str:
        return str(text).replace("\n", "<br>") if text is not None else ""
    
    tables_html = ""
    for i, table in enumerate(tables):
        table_rows = ""
        for row in table.get('data', []):
            table_rows += f"<tr>{''.join(f'<td>{format_cell_text(cell)}</td>' for cell in row)}</tr>"
        
        tables_html += f"""
        <div class="table-wrapper">
            <div class="table-container" id="table-container-{i}">
                <h2 class="neon-title">{table.get('title', 'Без названия')}</h2>
                
                <div class="controls">
                    <div class="search-container">
                        <input type="text" class="search-input" placeholder="Search in table..." 
                               data-table-id="{i}" id="searchInput-{i}">
                    </div>
                    <button class="edit-mode-btn" data-table-id="{i}" id="editModeBtn-{i}">
                        Edit mode...
                    </button>
                </div>
                
                <table class="neon-table" id="neonTable-{i}">
                    <thead>
                        <tr>
                            {''.join(f'<th>{col}</th>' for col in table.get('columns', []))}
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DoxUB results for '{search}'</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        body {{
            background-color: #0a0a1a;
            color: #e0e0ff;
            font-family: 'Orbitron', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            overflow-x: hidden;
        }}
        
        .main-title {{
            font-size: 3rem;
            margin-bottom: 30px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #fff;
            text-shadow: 
                0 0 5px #fff,
                0 0 10px #fff,
                0 0 20px #0ff,
                0 0 40px #0ff,
                0 0 80px #0ff;
        }}
        
        .table-wrapper {{
            width: 100%;
            display: flex;
            justify-content: center;
            margin-bottom: 50px;
        }}
        
        .table-container {{
            width: 100%;
            max-width: 1000px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .neon-title {{
            font-size: 2rem;
            margin-bottom: 20px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #fff;
            text-shadow: 
                0 0 5px #fff,
                0 0 10px #fff,
                0 0 15px #0ff,
                0 0 30px #0ff;
        }}
        
        .controls {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            margin-bottom: 20px;
            gap: 20px;
        }}
        
        .search-container {{
            flex-grow: 1;
        }}
        
        .edit-mode-btn {{
            background-color: rgba(0, 255, 255, 0.2);
            color: #0ff;
            border: 1px solid #0ff;
            border-radius: 5px;
            padding: 0 20px;
            cursor: pointer;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
        }}
        
        .edit-mode-btn:hover {{
            background-color: rgba(0, 255, 255, 0.4);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }}
        
        .edit-mode-btn.active {{
            background-color: rgba(0, 255, 255, 0.6);
            font-weight: bold;
        }}
        
        .search-input {{
            width: 100%;
            padding: 12px 20px;
            background-color: rgba(20, 30, 50, 0.7);
            border: 1px solid #0ff;
            border-radius: 5px;
            color: #fff;
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
            transition: all 0.3s;
        }}
        
        .search-input:focus {{
            outline: none;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }}
        
        .neon-table {{
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5),
                        0 0 20px rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }}
        
        .neon-table::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #0ff, #f0f, #0ff, #f0f, #0ff);
            background-size: 400%;
            z-index: -1;
            border-radius: 12px;
            opacity: 0.7;
            animation: animate-border 8s linear infinite;
        }}
        
        .neon-table th {{
            background-color: rgba(10, 20, 40, 0.9);
            color: #0ff;
            padding: 15px;
            text-align: left;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-bottom: 2px solid #0ff;
            position: relative;
            overflow: hidden;
        }}
        
        .neon-table th::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #0ff, transparent);
            animation: shine 3s infinite;
        }}
        
        .neon-table td {{
            padding: 12px 15px;
            background-color: rgba(20, 30, 50, 0.7);
            border-bottom: 1px solid rgba(0, 255, 255, 0.1);
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
            user-select: none;
            white-space: pre-line;
        }}
        
        .neon-table td.editable {{
            cursor: text;
            white-space: pre-wrap;
        }}
        
        .neon-table tr:hover td {{
            background-color: rgba(30, 40, 70, 0.9);
            color: #fff;
            text-shadow: 0 0 5px #fff;
        }}
        
        .neon-table td:focus {{
            outline: none;
            background-color: rgba(40, 50, 90, 0.9);
            border: 1px solid #0ff;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }}
        
        .neon-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .copy-notification {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 255, 255, 0.9);
            color: #0a0a1a;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.7);
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
        }}
        
        @keyframes animate-border {{
            0% {{ background-position: 0 0; }}
            50% {{ background-position: 300% 0; }}
            100% {{ background-position: 0 0; }}
        }}
        
        @keyframes shine {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .particles {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }}
        
        .particle {{
            position: absolute;
            background: rgba(0, 255, 255, 0.5);
            border-radius: 50%;
            animation: float linear infinite;
        }}
        
        @keyframes float {{
            0% {{
                transform: translateY(0) translateX(0);
                opacity: 1;
            }}
            100% {{
                transform: translateY(-1000px) translateX(200px);
                opacity: 0;
            }}
        }}
    </style>
</head>
<body>
    <h1 class="main-title">DoxUB results for '{search}'</h1>
    
    <div class="particles" id="particles"></div>
    
    {tables_html}
    
    <div class="copy-notification" id="copyNotification">Copied!</div>
    
    <script>
        // Создание частиц для фона
        function createParticles() {{
            const container = document.getElementById('particles');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {{
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                const size = Math.random() * 5 + 1;
                const posX = Math.random() * window.innerWidth;
                const delay = Math.random() * 5;
                const duration = Math.random() * 15 + 10;
                
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = posX + 'px';
                particle.style.bottom = '-10px';
                particle.style.animationDelay = delay + 's';
                particle.style.animationDuration = duration + 's';
                
                container.appendChild(particle);
            }}
        }}
        
        function setupCopyToClipboard() {{
            const cells = document.querySelectorAll('.neon-table td');
            const notification = document.getElementById('copyNotification');
            
            cells.forEach(cell => {{
                cell.addEventListener('click', (e) => {{
                    if (cell.classList.contains('editable')) return;
                    
                    const text = cell.textContent || cell.innerText;
                    navigator.clipboard.writeText(text).then(() => {{
                        notification.style.opacity = '1';
                        setTimeout(() => {{
                            notification.style.opacity = '0';
                        }}, 2000);
                    }});
                }});
            }});
        }}
        
        function setupSearch() {{
            const searchInputs = document.querySelectorAll('.search-input');
            
            searchInputs.forEach(input => {{
                const tableId = input.getAttribute('data-table-id');
                const table = document.getElementById(`neonTable-${{tableId}}`);
                const rows = table.querySelectorAll('tbody tr');
                
                input.addEventListener('input', () => {{
                    const searchTerm = input.value.toLowerCase();
                    
                    rows.forEach(row => {{
                        const cells = row.querySelectorAll('td');
                        let found = false;
                        
                        cells.forEach(cell => {{
                            const text = (cell.textContent || cell.innerText).toLowerCase();
                            if (text.includes(searchTerm)) {{
                                found = true;
                            }}
                        }});
                        
                        row.style.display = found ? '' : 'none';
                    }});
                }});
            }});
        }}
        
        function setupEditMode() {{
            const editButtons = document.querySelectorAll('.edit-mode-btn');
            
            editButtons.forEach(btn => {{
                const tableId = btn.getAttribute('data-table-id');
                const table = document.getElementById(`neonTable-${{tableId}}`);
                const cells = table.querySelectorAll('td');
                
                btn.addEventListener('click', () => {{
                    btn.classList.toggle('active');
                    const isEditMode = btn.classList.contains('active');
                    
                    cells.forEach(cell => {{
                        if (isEditMode) {{
                            cell.classList.add('editable');
                            cell.setAttribute('contenteditable', 'true');
                            cell.style.whiteSpace = 'pre-wrap';
                        }} else {{
                            cell.classList.remove('editable');
                            cell.removeAttribute('contenteditable');
                            cell.blur();
                            cell.style.whiteSpace = 'pre-line';
                        }}
                    }});
                }});
            }});
        }}
        
        window.onload = function() {{
            createParticles();
            setupCopyToClipboard();
            setupSearch();
            setupEditMode();
        }};
    </script>
</body>
</html>
    """
    return html

@client.on_message()
async def message_handler(client: pyrogram.Client, message: pyrogram.types.Message):
    if message.text and message.text == ".download":
        if not message.reply_to_message:
            await message.edit_text("<b>Please answer.</b>")
            return
        
        if not message.reply_to_message.document:
            await message.edit_text("<b>Please respond to the document.</b>")
            return

        if not (message.reply_to_message.document.mime_type in ["text/comma-separated-values", "text/csv", "text/plain"]):
            await message.edit_text("<b>Please respond to the txt/csv document.</b>")
            return
        
        await message.edit_text("<b>Start downloading...</b>")
        await message.reply_to_message.download(f"base/{message.reply_to_message.document.file_name}")
        await message.edit_text("<b>Downloaded!</b>")

    if message.text and message.text == ".doxub":
        await message.edit_text("⚡ DoxUB Ultra-Fast Search\n\n.search [word] - search in database (1GB in 3-6s)\n.download - Download file to folder with bases")
    
    if message.text and message.text.split()[0].lower() == ".search":
        if len(message.text.split()) == 1:
            await message.edit_text("<i>Example: <code>.search +79999999999</code></i>")
            return

        if not os.path.exists("base"):
            os.makedirs("base")
            await message.edit_text("<b>Created 'base' directory. Add files there first.</b>")
            return

        files = [os.path.join("base", f) for f in os.listdir("base") if f.endswith((".csv", ".txt", ".dat", ".log"))]
        
        if not files:
            await message.edit_text("<b>No searchable files found in 'base' directory.</b>")
            return
        
        search_query = ' '.join(message.text.split()[1:])
        pattern = re.escape(search_query)
        
        stime = datetime.datetime.now()
        msg = await message.edit_text(f"⚡ Searching in {len(files)} files...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tables = []
            for file in files:
                file_size = os.path.getsize(file)
                if file_size > 1024 * 1024 * 100:
                    tables.append(executor.submit(process_large_file, file, pattern))
                else:
                    tables.append(executor.submit(ultra_fast_search, file, pattern))
            
            results = []
            for future in tables:
                if future.result() != None: results.append(future.result())

        elapsed = (datetime.datetime.now() - stime).total_seconds()
        total_size = sum(os.path.getsize(f) for f in files) / (1024 * 1024 * 1024)
        
        if not results:
            await msg.edit_text(f"🔍 No results found for <code>{search_query}</code>\n"
                              f"Processed {len(files)} files ({total_size:.2f} GB) in {elapsed:.2f}s")
            return
        len_results = 0
        nresults = []
        for i in results:
            len_results += len(i["data"])
            nresult = i
            nresult["data"] = nresult["data"][:100]
            nresults.append(nresult)
        await msg.edit_text(f"⚡ Found {len_results} results in {len(files)} files ({total_size:.2f} GB)\n"
                          f"Search time: {elapsed:.2f}s")

        batch_ = nresults[:5]
        batch = []
        for i in batch_:
            a = "\n".join([f"{key.capitalize()}: {value}" for key, value in zip(i["columns"], i["data"])])
            batch.append(f"<b>File: <code>{i["title"]}</code></b>\n\n<code>{a}</code>")
        response = "\n\n──────\n\n".join(batch)
        await client.send_message(message.chat.id, f"🔍 Files 1-5:\n\n{response}")

        html_output = generate_html_tables(nresults, search_query)
        with open(f"result_{search_query}.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        await message.reply_document(f"result_{search_query}.html")
        os.remove(f"result_{search_query}.html")

async def main():
    await client.start()
    os.system("cls" if platform.system().lower()[0] != "l" else "clear")
    print("⚡ Ultra-Fast DoxUB started")
    await idle()

client.run(main())
