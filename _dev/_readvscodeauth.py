# -*- coding: utf-8 -*-
import sqlite3, json

db = r"C:\Users\bonda\AppData\Roaming\Code\User\globalStorage\state.vscdb"
c = sqlite3.connect(db)
rows = c.execute(
    "SELECT key, value FROM ItemTable WHERE value LIKE '%bonditog%' OR key LIKE '%account%'"
).fetchall()
for k, v in rows:
    kk = k if isinstance(k, str) else k.decode('utf-8')
    vv = v if isinstance(v, str) else v.decode('utf-8', 'replace')
    print("KEY:", kk[:200])
    print("VAL:", vv[:1200])
    print("---")