from fasthtml.common import *
from taxonomy import taxonomies
import sqlite_minutils


db = database('data/paperlab.db')
dt = db.t

try:
    dt.user.drop()
    dt.category.drop()
    dt.paper.drop()
    print('tables dropped')
except sqlite_minutils.db.AlterError as e:
    pass

# INITIALIZE USER TABLE
dt.user.create(id=int, name=str, pwd=str, pk='id')
user = dt.user

# INITIALIZE CATEGORY TABLE
dt.category.create(code=str, name=str, pk='code')
category = dt.category

# INITIALIZE PAPER TABLE
dt.paper.create(id=int, title=str, category_code=str, user_id=int, pk='id')
db['paper'].add_foreign_key('category_code','category','code')
db['paper'].add_foreign_key('user_id','user','id')
paper = dt.paper

print(f'user table: {user.c}')
print(f'category table: {category.c}')
print(f'paper table: {paper.c}')

for code, name in taxonomies.items():
    category.insert(code=code, name=name)

query = 'SELECT * FROM category'
print(db.q(query))

