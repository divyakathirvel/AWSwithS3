import os
import string

import botocore
from flask import Flask, jsonify
import boto3
from botocore.client import Config
from flask import render_template
from flask import request

ACCESS_KEY_ID = '<access-key>'
ACCESS_SECRET_KEY = '<access-secret-key>'
BUCKET_NAME = '<bucket-name>'

app = Flask(__name__)

# S3 Connect
s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
print('Connected')

@app.route('/')
def main():
    return render_template('login1.html')
	
# To allow user to login by validating against a text file
@app.route('/login', methods=['POST', 'GET'])
def login():
	# place text file in the Bucket
    key = 'login_1.txt'
    bucket = s3.Bucket('BUCKET_NAME')
    print bucket
    for bucket in s3.buckets.all():
        print bucket
        for object in bucket.objects.all():
            if key == object.key:
                body = object.get()['Body'].read()
                username = request.form['username']
                password = request.form['password']
                username, password = body.split(':')
                if request.form['username'] == username and request.form['password'] == password:
                    print('Successful')
                    return render_template('index.html')
                else:
                    return "Login Failed!!"

# To list all the Image files in the Bucket along with comments stored in text file
@app.route('/list', methods=['POST'])
def list():
    obj1 = ''
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            objfile = object.key.split('.')[0]
            objext = object.key.split('.')[1]
            print objfile, objext
            if (objext == 'jpg'):
                objfile += '_c.txt'
                for bucket in s3.buckets.all():
                    for inobj in bucket.objects.all():
                        if (objfile == inobj.key):
                            body = inobj.get()['Body'].read()
                            obj1 = obj1 + '</br>' + 'Name ' + object.key + '\t Size ' + str(
                                object.size) + 'Bytes' + '\t Last Modified ' + str(
                                object.last_modified) + '\t Contents' + body
                            obj1 += '</br>'
                            print obj1
    return obj1

# To delete a particular file name upon user request
@app.route('/delete', methods=['POST'])
def delete():
    file_name = request.form['filename']
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            if object.key == file_name:
                object.delete()
                return "File has been deleted successfully"

# Allow user to enter File name and upload the file
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_name = file.filename
    content = file.read()
    number = request.form['numb']
    numfile = file_name.split('.')[0]
    numfile = numfile + '_' + number + '.txt'
    s3.Bucket('mydinbucket').put_object(Key=numfile, Body=content, ACL='public-read')
    return "Successfully uploaded"

# To display the contents in the file
@app.route('/display', methods=['POST', 'GET'])
def display():
    number = request.form['file']
    bucket = s3.Bucket('BUCKET_NAME')
    print bucket
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            val = object.key
            print val
            file = val.split('.')[0]
            value = file.split('_')[1]
            print file,value
            if value == number:
                body = object.get()['Body'].read()
                return '<p>' + body + '</p>'

# To allow user to enter a range of number and list all files in that range
@app.route('/range', methods=['POST', 'GET'])
def range():
    fnumber = request.form['from']
    tnumber=request.form['to']
    bucket = s3.Bucket('BUCKET_NAME')
    body=''
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            val = object.key
            file = val.split('.')[0]
            value = file.split('_')[1]
            mid=fnumber+1
            if value == fnumber:
                body += '<br>' + object.get()['Body'].read() + '</br>'
    return '<p>' + body + '</p>'

# To allow a user to enter filename and download the file
@app.route('/download', methods=['POST'])
def download():
    KEY = request.form['filename']
    commentfile = KEY.split('.')[0]
    commentfile += '_c.txt'
    for bucket in s3.buckets.all():
        for inobj in bucket.objects.all():
            if (commentfile == inobj.key):
                print ('hi')
                body = inobj.get()['Body'].read()
                href = 'https://s3.us-east-2.amazonaws.com/mydinbucket/%s' % KEY
                return body + "<a href=%s>Link</a>" % href
			else:
				return "File not available"

if __name__ == "__main__":
    app.run(host='localhost', port='8997')
