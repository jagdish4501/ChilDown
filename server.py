import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib
import json
import cherrypy
import os
import ast
from dotenv import load_dotenv
# load environment variables from .env file
load_dotenv()
# load blog from api
blog = []
with open('blog.json') as f:
    blog = json.load(f)

# creating Flask app
app = Flask(__name__)


# loading model from pkl and required function from ML model
model_svm = joblib.load('ML_Model/svm_model.pkl')
model_npl = joblib.load('ML_Model/nlp_model.pkl')
count_vectorizer = joblib.load('ML_Model/cnt_vec.pkl')


# minimum attribute value in svm_model
mn = ast.literal_eval(os.environ.get('Min'))

# differece of max and min attribute value
dif = ast.literal_eval(os.environ.get('Diff'))

# bare minimum condition
bare_min = ast.literal_eval(os.environ.get('Bare_Min'))

#
CauseOfDepresion = ast.literal_eval(os.environ.get('Leval_dep'))


@app.route('/chilDown')
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/describe', methods=['GET', 'POST'])
def describe():
    if request.method == 'GET':
        return render_template('desc.html')
    elif request.method == 'POST':
        data = [request.form['situation']]
        data = pd.Series(data)
        cv = count_vectorizer.transform(data)
        print(cv.shape)
        pred = model_npl.predict(cv)
        print(pred)
        return render_template('blog.html', prediction_text='Stress Genrated DueTo : {}'.format(CauseOfDepresion[pred[0]]))
    else:
        return "Method Not Allowed"


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('form.html')
    elif request.method == 'POST':
        responsible_idx = []
        data = [float(x) for x in request.form.values()]
        for idx in range(20):
            if data[idx]-bare_min[idx] < 0:
                responsible_idx.append(idx)
        for idx in range(20):
            data[idx] = (data[idx]-mn[idx])/dif[idx]
        final_features = np.array(data).reshape(1, -1)
        prediction = model_svm.predict(final_features)
        prediction_list = prediction.tolist()
        local_blog = []
        # print(len(responsible_idx))
        for idx in range(len(responsible_idx)):
            local_blog.append(blog['blog'][prediction_list[0]]
                              [responsible_idx[idx]])
        return render_template('blog.html', prediction_text='Stress level $ {}'.format(prediction_list), responsible_atribute_for_stress=local_blog)
    else:
        return 'methode not allowed'


# About us route
@app.route('/AboutUs', methods=['GET', 'POST'])
def AboutUs():
    if request.method == 'GET':
        return render_template('AboutUs.html')
    elif request.method == 'POST':
        return render_template('AboutUs.html')
    else:
        return 'methode not allowed'

    # cherrypy code


class EmbeddedApp(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


# (your Flask routes and other code remain the same)
if __name__ == "__main__":
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
    })
    cherrypy.tree.graft(EmbeddedApp(app), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
