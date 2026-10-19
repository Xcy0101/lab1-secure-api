from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "change‑this‑to‑a‑strong‑secret‑key‑here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)

# 用户数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.LargeBinary)


with app.app_context():
    db.create_all()
    # 测试账号，密码test123
    if not User.query.filter_by(username="testuser").first():
        hash_pw = bcrypt.hashpw(b"test123", bcrypt.gensalt())
        new_user = User(username="testuser", password_hash=hash_pw)
        db.session.add(new_user)
        db.session.commit()


# 首页路由，解决浏览器访问根路径404
@app.route('/')
def index():
    return jsonify({
        "message": "Secure API server running",
        "endpoints": [
            "POST /auth/login",
            "GET /api/data",
            "GET /api/userinfo"
        ]
    })


# 1.登录接口 POST /auth/login
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode("utf‑8"), user.password_hash):
        token = create_access_token(identity=username)
        return jsonify(access_token=token), 200
    return jsonify(msg="Invalid credentials"), 401


# 2.受保护接口 GET /api/data
@app.route("/api/data", methods=["GET"])
@jwt_required()
def get_data():
    current_user = get_jwt_identity()
    resp_data = {"user": current_user, "data_list": ["item1", "item2", "item3"]}
    return jsonify(resp_data)


# 3.自己新增接口：GET /api/userinfo
@app.route("/api/userinfo", methods=["GET"])
@jwt_required()
def user_info():
    username = get_jwt_identity()
    return jsonify(username=username, note="protected user profile")


if __name__ == "__main__":
    app.run(debug=False)
