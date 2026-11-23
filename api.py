# 🔥 Flask basic import (server banane ke liye)
from flask import Flask , request

# 🔥 Database handle karne ke liye ORM (Object Relational Mapping)
from flask_sqlalchemy import SQLAlchemy

# 🔥 REST API banane ke tools
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort 


# 🔥 Flask app initialize
app = Flask(__name__)


# =========================================================
# 🔐 MIDDLEWARE (VERY IMPORTANT CONCEPT)
# =========================================================

# 👉 BEFORE REQUEST (Request aane se pehle chalega)
@app.before_request
def auth_middleware():

    # 👉 Agar request /api se start nahi ho rahi (normal webpage hai)
    if not request.path.startswith("/api"):
        return   # kuch mat karo

    # 👉 Header se Authorization token nikalo
    token = request.headers.get("Authorization")

    # 👉 Agar token galat hai
    if token != "12345":
        return {"message":"unauthorized"} , 401   # error return karo


# 👉 AFTER REQUEST (Response jaane se pehle chalega)
@app.after_request
def after_middleware(output):

    # 👉 Status code print karo (200, 404, etc.)
    print(output.status_code)

    # 👉 Response me ek extra header add kar diya
    output.headers["test"] = "ok"

    return output   # modified response return karo


# =========================================================
# 🗄 DATABASE CONFIGURATION
# =========================================================

# 👉 SQLite database (local file me banega)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# 👉 Extra tracking band kiya (performance ke liye)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 👉 DB initialize
db = SQLAlchemy(app)

# 👉 API initialize (Flask ko REST API bana diya)
api = Api(app)


# =========================================================
# 🧱 MODEL (DATABASE TABLE)
# =========================================================

class UserModel(db.Model):

    # 👉 Primary key (unique id)
    id = db.Column(db.Integer, primary_key=True)

    # 👉 Name (unique hona chahiye, blank nahi hona chahiye)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # 👉 Email (unique + required)
    email = db.Column(db.String(80), unique=True, nullable=False)

    # 👉 Debug print ke liye (optional)
    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"


# =========================================================
# 📥 REQUEST PARSER (INPUT VALIDATION)
# =========================================================

user_args = reqparse.RequestParser()

# 👉 Name compulsory hai
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")

# 👉 Email compulsory hai
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")


# =========================================================
# 📤 OUTPUT FORMAT (Kya return karna hai)
# =========================================================

userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}


# =========================================================
# 🔥 ALL USERS API (/api/users/)
# =========================================================

class Users(Resource):

    # 👉 GET → sab users fetch karega
    @marshal_with(userFields)
    def get(self):

        # 👉 Database se saare users lao
        return UserModel.query.all()


    # 👉 POST → new user create karega
    @marshal_with(userFields)
    def post(self):

        # 👉 Client se data read karo
        args = user_args.parse_args()
        print("DATA RECEIVED:", args)

        # 👉 Check karo email already exist karta hai ya nahi
        existing_user = UserModel.query.filter_by(email=args["email"]).first()

        if existing_user:
            abort(409, message="User already exists")   # duplicate error

        # 👉 New user object banao
        user = UserModel(
            name=args["name"],
            email=args["email"]
        )

        # 👉 DB me save karo
        db.session.add(user)
        db.session.commit()

        print("USER SAVED:", user)

        return user, 201   # success response


# =========================================================
# 🔥 SINGLE USER API (/api/users/<id>)
# =========================================================

class User(Resource):

    # 👉 GET → ek specific user
    @marshal_with(userFields)
    def get(self, id):

        # 👉 ID se user dhundo
        user = UserModel.query.filter_by(id=id).first()

        # 👉 Agar user nahi mila
        if not user:
            abort(404, message="User not found")

        return user


    # 👉 PATCH → update user
    @marshal_with(userFields)
    def patch(self, id):

        # 👉 Input data lo
        args = user_args.parse_args()

        # 👉 User dhundo
        user = UserModel.query.filter_by(id=id).first()

        if not user:
            abort(404, message="User not found")

        # 👉 Update values
        user.name = args["name"]
        user.email = args["email"]

        # 👉 DB save
        db.session.commit()

        return user


    # 👉 DELETE → user delete karo
    @marshal_with(userFields)
    def delete(self, id):

        # 👉 User dhundo
        user = UserModel.query.filter_by(id=id).first()

        if not user:
            abort(404, message="User not found")

        # 👉 Delete user
        db.session.delete(user)
        db.session.commit()

        # 👉 Updated list return karo
        users = UserModel.query.all()

        return users, 200


# =========================================================
# 🔗 ROUTES (URL mapping)
# =========================================================

# 👉 All users ke liye
api.add_resource(Users, '/api/users/')

# 👉 Single user ke liye
api.add_resource(User, '/api/users/<int:id>')


# =========================================================
# 🌐 NORMAL ROUTE (Browser ke liye)
# =========================================================

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'


# =========================================================
# 🚀 SERVER RUN
# =========================================================

if __name__ == '__main__':
    # 👉 Debug ON (auto reload + error show)
    app.run(debug=True)