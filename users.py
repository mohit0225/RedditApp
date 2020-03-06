import sys
import flask_api
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI, status, exceptions
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = FlaskAPI(__name__) 

def get_db():
	db = getattr(g,'_database', None)
	if db is None:
		db = g._database = sqlite3.connect('reddit.db')
	return db

@app.route("/users",methods=['GET'])
def get_users():
	sqlQry = "select user_name,email,karma from users "
	db =  get_db()
	rs = db.execute(sqlQry)
	res = rs.fetchall()
	rs.close()
	return jsonify(list(res)), status.HTTP_200_OK

@app.route("/users",methods=['POST'])
def create_users():
	mandatory_fields = ['user_name','email','karma']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()
	
	try:
		user_name 	= request.data.get('user_name','')
		email 	= request.data.get('email','')
		karma	= request.data.get('karma','')
		
		sqlQry = "insert into users(user_name,email,karma) values ('%s','%s','%d')" %(user_name,email,karma)
		db = get_db()
		db.execute(sqlQry)
		db.commit()
		response  = Response(status=201)
		response.headers['location'] = '/users/'+user_name
		response.headers['status'] = '201 Created'

	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT

	return response, status.HTTP_201_CREATED

if __name__ == "__main__":
	app.run(debug=True)
	