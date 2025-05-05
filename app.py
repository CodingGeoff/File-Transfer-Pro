
# # app.py
# import sys
# import os
# from flask import Flask, render_template, request, flash, redirect

# import io
# import os
# import logging
# import sqlite3
# import unicodedata
# import re
# from datetime import datetime
# from urllib.parse import unquote
# from flask import Flask, render_template, request, send_from_directory, flash, redirect, g
# from werkzeug.utils import secure_filename as original_secure_filename
# from werkzeug.exceptions import RequestEntityTooLarge

# # Windows系统编码处理
# if sys.platform.startswith('win'):
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030', errors='replace')
#     sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='gb18030', errors='replace')

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# # 配置参数
# DATABASE = 'data.db'
# UPLOAD_FOLDER = 'files'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 500000000000000 * 1024 * 1024
# app.config['TEMPLATES_AUTO_RELOAD'] = True

# # 修改安全文件名处理函数
# def secure_filename(name):
#     # 保留路径分隔符但处理每个路径部分
#     return original_secure_filename(name)


# def secure_filepath(path):
#     # 统一路径分隔符并处理每个部分
#     path = path.replace('\\', '/')  # 统一使用正斜杠
#     parts = path.split('/')
#     safe_parts = []
#     for part in parts:
#         if part in ('', '.', '..'):
#             continue
#         safe_part = secure_filename(part)
#         if safe_part:
#             safe_parts.append(safe_part)
#     return os.path.join(*safe_parts)


# # 增强的安全文件名函数（支持中文）
# def original_secure_filename(filename):
#     _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_\u4e00-\u9fff\-\. ]')
#     _windows_device_files = ('CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3',
#                              'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1',
#                              'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9')

#     filename = unicodedata.normalize('NFKD', filename)
#     filename = filename.encode('utf-8', 'ignore').decode('utf-8')

#     for sep in os.path.sep, os.path.altsep:
#         if sep:
#             filename = filename.replace(sep, ' ')

#     filename = _filename_ascii_strip_re.sub('', filename).strip('._')

#     if os.name == 'nt' and os.path.splitext(filename)[0].upper() in _windows_device_files:
#         filename = f'_{filename}'

#     return filename


# # 数据库初始化
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#         db.row_factory = sqlite3.Row
#     return db


# @app.teardown_appcontext
# def close_db(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


# def init_db():
#     with app.app_context():
#         db = get_db()
#         db.execute('''
#             CREATE TABLE IF NOT EXISTS messages (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 content TEXT NOT NULL,
#                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#         db.commit()


# if not os.path.exists(DATABASE):
#     init_db()
# else:
#     init_db()

# # 配置日志
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler('app.log', encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )

# # 确保上传目录存在并有写入权限
# try:
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#     os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
# except Exception as e:
#     logging.critical(f"无法创建上传目录: {str(e)}")
#     exit(1)


# @app.route('/')
# def index():
#     def convert_size(size_bytes):
#         units = ('B', 'KB', 'MB', 'GB', 'TB')
#         if size_bytes == 0:
#             return "0B"
#         size = float(size_bytes)
#         for unit in units:
#             if size < 1024.0 or unit == units[-1]:
#                 break
#             size /= 1024.0
#         return f"{size:.2f} {unit}" if unit != 'B' else f"{int(size)}{unit}"

#     # files = []
#     # upload_dir = app.config['UPLOAD_FOLDER']
#     # try:
#     #     for filename in os.listdir(upload_dir):
#     #         filepath = os.path.join(upload_dir, filename)
#     #         if os.path.isfile(filepath):
#     #             files.append({
#     #                 'name': filename,
#     #                 'size': convert_size(os.path.getsize(filepath)),
#     #                 'date': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
#     #             })
#     # except Exception as e:
#     #     logging.error(f"读取文件列表失败: {str(e)}")
    
    
#     files = []
#     upload_dir = app.config['UPLOAD_FOLDER']
#     for root, dirs, filenames in os.walk(upload_dir):
#         for filename in filenames:
#             filepath = os.path.join(root, filename)
#             rel_path = os.path.relpath(filepath, upload_dir)
#             files.append({
#                 'name': rel_path,
#                 'size': convert_size(os.path.getsize(filepath)),
#                 'date': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
#             })
            
#     db = get_db()
#     messages = []
#     try:
#         messages = db.execute('''
#             SELECT content, strftime('%H:%M:%S', timestamp) as time 
#             FROM messages 
#             ORDER BY timestamp DESC 
#             LIMIT 2000
#         ''').fetchall()
#     except Exception as e:
#         logging.error(f"获取消息失败: {str(e)}")

#     return render_template('index.html', files=files, chat_messages=reversed(list(messages)))


# # @app.route('/upload', methods=['POST'])
# # def upload_file():
# #     try:
# #         if 'files' not in request.files:
# #             flash('请选择要上传的文件')
# #             return redirect('/')

# #         files = request.files.getlist('files')
# #         if not files or all(file.filename == '' for file in files):
# #             flash('未选择任何文件')
# #             return redirect('/')

# #         upload_count = 0
# #         error_messages = []

# #         for file in files:
# #             if not file or file.filename == '':
# #                 continue

# #             try:
# #                 original_name = file.filename
# #                 filename = secure_filename(original_name)
# #                 save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

# #                 if not os.path.abspath(save_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
# #                     raise ValueError("非法文件路径")

# #                 if os.path.exists(save_path):
# #                     raise FileExistsError("文件已存在")

# #                 file.save(save_path)
# #                 upload_count += 1
# #                 logging.info(f"文件上传成功: {original_name} -> {save_path}")

# #             except FileExistsError as e:
# #                 error_msg = f"文件已存在: {original_name}"
# #                 error_messages.append(error_msg)
# #                 logging.warning(error_msg)
# #             except Exception as e:
# #                 error_msg = f"上传失败: {original_name} ({str(e)})"
# #                 error_messages.append(error_msg)
# #                 logging.error(error_msg, exc_info=True)

# #         if upload_count > 0:
# #             flash(f'成功上传 {upload_count} 个文件')
# #         if error_messages:
# #             flash('部分错误: ' + '，'.join(error_messages[:3]))

# #         return redirect('/')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     try:
#         if 'files' not in request.files:
#             flash('请选择文件')
#             return redirect('/')

#         files = request.files.getlist('files')
#         upload_count = 0
#         error_messages = []

#         for file in files:
#             if file.filename == '':
#                 continue

#             try:
#                 # 处理文件路径
#                 relative_path = secure_filepath(file.filename)
#                 save_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)

#                 # 安全检查
#                 if not os.path.abspath(save_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
#                     raise ValueError("非法文件路径")

#                 # 创建目录并保存文件
#                 os.makedirs(os.path.dirname(save_path), exist_ok=True)
#                 file.save(save_path)
#                 upload_count += 1
#                 logging.info(f"文件保存成功: {save_path}")

#             except Exception as e:
#                 error_msg = f"{file.filename} 上传失败: {str(e)}"
#                 error_messages.append(error_msg)
#                 logging.error(error_msg, exc_info=True)

#         if upload_count > 0:
#             flash(f'成功上传 {upload_count} 个文件')
#         if error_messages:
#             flash('部分错误: ' + '，'.join(error_messages[:3]))

#         return redirect('/')
    
#     except RequestEntityTooLarge:
#         flash('文件总大小超过500MB限制')
#         return redirect('/')
#     except Exception as e:
#         logging.critical(f"上传处理失败: {str(e)}", exc_info=True)
#         flash('服务器内部错误')
#         return redirect('/')


# @app.route('/download/<path:filename>')
# def download_file(filename):
#     try:
#         decoded_name = unquote(filename)
#         safe_name = secure_filename(decoded_name)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)

#         if not os.path.isfile(file_path):
#             flash('文件不存在')
#             return redirect('/')

#         return send_from_directory(
#             app.config['UPLOAD_FOLDER'],
#             safe_name,
#             as_attachment=True,
#             download_name=safe_name,
#             mimetype='application/octet-stream'
#         )
#     except Exception as e:
#         logging.error(f"下载失败: {str(e)}", exc_info=True)
#         flash('文件下载失败')
#         return redirect('/')


# @app.route('/chat', methods=['POST'])
# def chat():
#     message = request.form.get('message', '')[:200000000000000].strip()
#     if message:
#         try:
#             db = get_db()
#             db.execute('INSERT INTO messages (content) VALUES (?)', (message,))
#             db.commit()
#         except Exception as e:
#             db.rollback()
#             logging.error(f"消息保存失败: {str(e)}")
#     return redirect('/')


# @app.route('/get_messages')
# def get_messages():
#     try:
#         messages = get_db().execute('''
#             SELECT content, strftime('%H:%M:%S', timestamp) as time 
#             FROM messages 
#             ORDER BY timestamp DESC 
#             LIMIT 20
#         ''').fetchall()
#         return {'messages': [dict(msg) for msg in reversed(messages)]}
#     except Exception as e:
#         logging.error(f"消息获取失败: {str(e)}")
#         return {'messages': []}


# @app.errorhandler(413)
# def request_entity_too_large(error):
#     flash('文件大小超过限制')
#     return redirect('/')

import sys
import io
import os
import logging
import sqlite3
import unicodedata
import re
from datetime import datetime
from urllib.parse import unquote
from flask import Flask, render_template, request, send_from_directory, flash, redirect, g
from werkzeug.utils import secure_filename as original_secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Windows系统编码处理
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='gb18030', errors='replace')

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 配置参数
DATABASE = 'data.db'
UPLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 安全文件名处理
def secure_filename(name):
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_\u4e00-\u9fff\-\. ]')
    name = unicodedata.normalize('NFKD', name).encode('utf-8', 'ignore').decode('utf-8')
    name = _filename_ascii_strip_re.sub('', name).strip('._')
    return name

def secure_filepath(path):
    path = path.replace('\\', '/')
    parts = [secure_filename(p) for p in path.split('/') if p not in ('', '.', '..')]
    return os.path.join(*parts)

# 数据库处理
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

if not os.path.exists(DATABASE):
    init_db()
else:
    init_db()

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 创建上传目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    def convert_size(size):
        units = ('B', 'KB', 'MB', 'GB')
        for unit in units:
            if size < 1024.0 or unit == 'GB':
                break
            size /= 1024.0
        return f"{size:.1f} {unit}"

    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    for root, _, filenames in os.walk(upload_dir):
        for name in filenames:
            path = os.path.join(root, name)
            rel_path = os.path.relpath(path, upload_dir)
            files.append({
                'name': rel_path.replace('\\', '/'),
                'size': convert_size(os.path.getsize(path)),
                'date': datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
            })

    db = get_db()
    messages = db.execute('''
        SELECT content, strftime('%H:%M', timestamp) as time
        FROM messages ORDER BY timestamp DESC LIMIT 20
    ''').fetchall()

    return render_template('index.html', 
                         files=sorted(files, key=lambda x: x['date'], reverse=True),
                         chat_messages=messages)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            flash('请选择文件')
            return redirect('/')

        files = request.files.getlist('files')
        upload_count = 0
        error_messages = []

        for file in files:
            if not file or file.filename == '':
                continue

            try:
                safe_path = secure_filepath(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_path)
                
                if not os.path.abspath(save_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
                    raise ValueError("非法路径")

                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                upload_count += 1
            except Exception as e:
                error_messages.append(f"{file.filename}: {str(e)}")

        if upload_count > 0:
            flash(f'成功上传 {upload_count} 个文件')
        if error_messages:
            flash('错误文件: ' + ', '.join(error_messages[:3]))

        return redirect('/')
    
    except RequestEntityTooLarge:
        flash('文件大小超过限制')
        return redirect('/')
    except Exception as e:
        logging.error(f"上传错误: {str(e)}")
        flash('服务器错误')
        return redirect('/')

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        safe_path = secure_filepath(filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_path)
        
        if not os.path.exists(full_path):
            flash('文件不存在')
            return redirect('/')

        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            safe_path,
            as_attachment=True,
            download_name=os.path.basename(safe_path)
        )
    except Exception as e:
        logging.error(f"下载失败: {str(e)}")
        flash('下载错误')
        return redirect('/')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '')[:200].strip()
    if message:
        try:
            db = get_db()
            db.execute('INSERT INTO messages (content) VALUES (?)', (message,))
            db.commit()
        except Exception as e:
            db.rollback()
    return redirect('/')

@app.route('/get_messages')
def get_messages():
    db = get_db()
    messages = db.execute('''
        SELECT content, strftime('%H:%M', timestamp) as time
        FROM messages ORDER BY timestamp DESC LIMIT 20
    ''').fetchall()
    return {'messages': [dict(m) for m in messages]}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)