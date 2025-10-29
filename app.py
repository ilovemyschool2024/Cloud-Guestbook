import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# --- 关键配置：改为 SQLite ---

# 获取当前文件 (app.py) 所在的目录
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# 配置数据库 URI
# 这会在您的项目根目录下创建一个名为 guestbook.db 的文件
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'guestbook.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 数据库模型 (无需任何改动) ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80))
    text = db.Column(db.String(200))

# --- 路由和视图 (无需任何改动) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        author = request.form['author']
        text = request.form['text']
        
        if not author:
            author = "匿名"
        
        new_message = Message(author=author, text=text)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('index'))

    # 在应用上下文中创建数据库表（如果它们还不存在）
    # 这是一个简单的方法，确保在首次访问时创建表
    with app.app_context():
        db.create_all()
        
    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
    # 注意：在上面的 index 路由中，我们已经添加了 db.create_all()
    # 这样更自动化，但保留传统的初始化方法仍然是好习惯。
    # 部署时，确保在启动应用前至少运行一次初始化。
    
    # 确保在ECS上使用 0.0.0.0 使其可以被公网访问
    app.run(host='0.0.0.0', port=5000)