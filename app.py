from flask import Flask, session, render_template, request, redirect, url_for
from openai import OpenAI
import json
import os 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = 'secret123'

# 로그인 페이지
@app.route('/')
def home():
    return render_template('login.html')

# 로그인 처리
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == "admin" and password == "1234":
        return redirect(url_for('board'))
    else:
        return "로그인 실패"

if os.path.exists('posts.json'):
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
else:
    posts = []
def save_posts():
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# 글삭제
@app.route('/delete/<int:post_id>')
def delete(post_id):
    posts.pop(post_id)
    save_posts()
    return redirect(url_for('board'))

# 글 수정
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = posts[post_id]

    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')
        save_posts()
        return redirect(url_for('board'))
    

    return render_template('edit.html', post=post, post_id=post_id)

# 검색 기능
@app.route('/board', methods=['GET', 'POST'])
def board():
    query = request.args.get('q', '')

    filtered_posts = posts
    if query:
        filtered_posts = [
            p for p in posts
            if query.lower() in p['title'].lower()
        ]

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        posts.append({
            "title": title,
            "content": content,
            "comments": []
        })
        save_posts()
        return redirect(url_for('board'))
    return render_template('board.html', posts=filtered_posts)
# 댓글 기능
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    comment = request.form.get('comment')

    posts[post_id]["comments"].append(comment)
    save_posts()
    return redirect(url_for('board'))

# 챗봇 (고객센터)
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        message = request.form.get('message')

        # 사용자 메시지 저장
        session['chat_history'].append({
            "role": "user",
            "content": message
        })

        # OpenAI 호출
        try:
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=session['chat_history']
            )
            response = completion.choices[0].message.content

        except Exception as e:
            print(e)
            response = "⚠️ AI 서버 오류 또는 사용량 초과"


        # 응답 저장
        session['chat_history'].append({
            "role": "assistant",
            "content": response
        })

        session.modified = True

    return render_template('chatbot.html', chat_history=session['chat_history'])

if __name__ == '__main__':
    app.run(debug=True)