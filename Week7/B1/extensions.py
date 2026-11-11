from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api

# Module-level proxy, chưa gắn app — chờ init_app() qua factory
# (slide 10/16: "Extension và Blueprint — tổ chức ứng dụng Flask với Application Factory")
db = SQLAlchemy()
api = Api()
