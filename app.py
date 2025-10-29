import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- 关键配置：连接到您的华为云RDS ---
# 从环境变量获取数据库信息，如果获取不到，则使用默认值（用于本地测试）
DB_USER = os.environ.get('DB_USER', 'your_rds_username')
DB_PASS = os.environ.get('DB_PASS', 'your_rds_password')
DB_HOST = os.environ.get('DB_HOST', 'your_rds_internal_address')
DB_NAME = os.environ.get('DB_NAME', 'your_rds_database_name')

# 确保使用 pymysql 作为驱动
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 数据库模型 ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80))
    text = db.Column(db.String(200))

# --- 路由和视图 ---
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

    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
    # 第一次运行时，在Python环境中执行 db.create_all() 来创建表
    # 例如：
    # from app import app, db
    # with app.app_context():
    #     db.create_all()
    #
    # 确保在ECS上使用 0.0.0.0 使其可以被公网访问
    app.run(host='0.0.0.0', port=5000)