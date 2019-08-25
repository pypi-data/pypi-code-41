import jwt, sqlite3, hashlib
from flask_restful import Resource
from flask import request, g, make_response, abort, jsonify

def _where(keys, action=' WHERE ', j=' AND ',op='='):
	return action + j.join([k+op+(v.decode() if type(v) is bytes else '?') for (k,v) in keys.items()]) if keys else ''
def _values(keys):
	return [v for v in keys.values() if type(v) in (str,int)]
def _order(by):
	return f' ORDER BY {by[0]} {by[1]}' if by else ''

class Sqlt(object):
	def to_db(self, vals):
		for k,v in list(vals.items()):
			if k == '_password': vals[k] = hashlib.sha1(str(self.salt + v).encode('utf-8')).hexdigest()
			if k.endswith('List'): vals[k] = '\n'.join(v) if v else []
		return vals
	def from_db(self, cols):
		for k,v in list((cols or {}).items()):
			if k.startswith('_'): del cols[k]
			if k.endswith('List'): cols[k] = list(filter(None, v.split('\n'))) if v else []
		return cols
	def __init__(self, path, salt):
		self.conn = sqlite3.connect(path)
		self.salt = salt
#		self.conn.set_trace_callback(print)
		self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.cur = self.conn.cursor()
	def __del__(self):
		self.conn.commit()
		self.conn.close()
	def _commit(self):
		self.conn.commit()
	def _create(self, table, **cols):
		cols = ','.join([k+' '+v for (k,v) in cols.items()])
		self.cur.execute(f"CREATE TABLE {table}({cols});")
		return self if self.cur.arraysize else None

	def update(self, table, keys=dict(), cond=dict()):
		keys = self.to_db(keys)
		self.cur.execute(f"UPDATE {table}" + _where(keys, ' SET ', ',') + ' ' + _where(cond), list(keys.values()) + list(cond.values()))
		return self.cur.rowcount
	def insert(self, table, keys=dict()):
		keys = self.to_db(keys)
		cols = ', '.join(keys.keys())
		vals = ',:'.join(keys.keys())
		self.cur.execute(f'INSERT INTO {table} ({cols}) VALUES (:{vals})', _values(keys))
		return self.cur.lastrowid
	def all(self, table, cond=dict(), order=None, **argp):
		cond = self.to_db(cond)
		rows = self.cur.execute(f"SELECT * FROM {table}" + _where(cond,**argp) + _order(order), _values(cond))
		return list(map(self.from_db, rows.fetchall()))
	def get(self, table, cond=dict()):
		cond = self.to_db(cond)
		row = self.cur.execute(f"SELECT * FROM {table}" + _where(cond), _values(cond))
		return self.from_db(row.fetchone())
	def delete(self, table, cond=dict()):
		self.cur.execute(f"DELETE FROM {table}" + _where(cond), _values(cond))
		return self.cur.rowcount

class Jwt(object):
	cookies = {'header': (False, 0), 'payload': (False, 1), 'signature': (True, 2)}
	@staticmethod
	def decode(secret, cookies, header=None):
		try:
			cookie = [cookies.get(name) for name,(http,i) in Jwt.cookies.items()]
			cookie = '.'.join(cookie) if all(cookie) else None
			header = header[len('Bearer '):] if header and header.startswith('Bearer ') else None
			return jwt.decode(cookie or header, secret, algorithms=['HS256'])
		except jwt.exceptions.DecodeError:
			abort(403)
	@staticmethod
	def flush():
		response = make_response("{}")
		for name, (http, _) in Jwt.cookies.items():
			response.set_cookie(name, '', httponly=http, expires=0)
		return response
	@staticmethod
	def encode(secret, payload):
		token = jwt.encode(payload, secret).decode("utf-8")
		response = make_response(jsonify(token))
		for name, (http, i) in Jwt.cookies.items():
			response.set_cookie(name, token.split('.')[i], httponly=http)
		return response

class Rest(Resource):
	def get(self, table, id=None):
		if id:
			return g.db.get(table,{"id":id}) or abort(404)
		if 'q' in request.args:
			return g.db.all(table, {table: request.args.get('q')}, op='MATCH')
		return g.db.all(table, dict(request.args))
	def post(self, table):
		vals = request.get_json(True)
		if hasattr(self, table+'_post'):
			vals = getattr(self,table+'_post')(vals) or abort(403)
		return g.db.insert(table, vals), 201
	def put(self, table, id):
		vals = request.get_json(True)
		where = {"id":id}
		if hasattr(self, table+'_put'):
			where = getattr(self,table+'_put')(id, vals) or abort(403)
		return g.db.update(table, vals, where) or abort(404)
	def delete(self, table, id):
		where = {"id":id}
		if hasattr(self, table+'_delete'):
			where = getattr(self,table+'_delete')(id) or abort(403)
		return g.db.delete(table, where) or abort(404)
