#!/usr/bin/env python3
import hashlib
import os
import time

import numpy as np
import tensorflow as tf
from flask import jsonify, render_template
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage

from factory import create_app
from models import PredictionResult

app = create_app()
CORS(app)
api = Api(app)

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

model_file = 'output_graph.pb'
label_file = 'output_labels.txt'
input_height = 299
input_width = 299
input_mean = 0
input_std = 255
input_layer = 'Placeholder'
output_layer = 'final_result'


def check_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(
            file_reader, channels=3, name="png_reader")
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(
            tf.image.decode_gif(file_reader, name="gif_reader"))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
    else:
        image_reader = tf.image.decode_jpeg(
            file_reader, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(
        dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)
    return result


def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


graph = load_graph(model_file)

input_name = "import/" + input_layer
output_name = "import/" + output_layer
input_operation = graph.get_operation_by_name(input_name)
output_operation = graph.get_operation_by_name(output_name)

sess = tf.Session(graph=graph)


def get_label(file_name):
    t = read_tensor_from_image_file(
        file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)
    results = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: t
    })

    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)
    result = {'category': labels[top_k[0]]}
    for i in top_k:
        human_string = labels[i]
        score = results[i]
        result[human_string] = int(round(float(score), 4) * 10000)

    return result


def allowed_file(filename):
    """判断filename是否有后缀以及后缀是否在app.config['ALLOWED_EXTENSIONS']中"""
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config[
        'ALLOWED_EXTENSIONS']


class Prediction(Resource):
    def get(self):
        predcit_get_parser = reqparse.RequestParser()

        predcit_get_parser.add_argument(
            'page',
            type=int,
            location=['json', 'args', 'headers'],
            required=False)
        predcit_get_parser.add_argument(
            'limit',
            type=int,
            location=['json', 'args', 'headers'],
            required=False)
        predcit_get_parser.add_argument(
            'category',
            type=str,
            location=['json', 'args', 'headers'],
            required=False)
        args = predcit_get_parser.parse_args()
        page = args.get('page')
        limit = args.get('limit')
        if not page:
            page = 1
        if not limit:
            limit = 20
        skip_num = (page - 1) * limit
        category = args.get('category')
        predictions = PredictionResult.objects().order_by(
            '-predict_time').skip(skip_num).limit(limit)

        if category:
            predictions = predictions.filter(category=category)

        data = [prediction.to_dict() for prediction in predictions]
        res = {
            'code': 200,
            'msg': 'success',
            'count': PredictionResult.objects.count(),
            'data': data
        }
        return jsonify(res)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=FileStorage, location='files',
                            help='you need upload a image file')
        args = parser.parse_args()
        file = args.get('file')
        if not allowed_file(file.filename):
            return jsonify({"msg": "wrong file type"})
        if not file:
            return jsonify({"msg": "fail"})
        ext = file.filename.split('.')[-1]
        upload_file_name = hashlib.md5(
            (file.filename + str(time.time())).encode('UTF-8')).hexdigest()[:16]
        upload_file_name = '.'.join([upload_file_name, ext])
        upload_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            upload_file_name
        )
        check_dir(app.config['UPLOAD_FOLDER'])
        file.save(upload_path)
        res = get_label(upload_path)
        prediction = PredictionResult()
        prediction.path = upload_path
        prediction.category = res.get('category')
        prediction.cataract = str(res.get('cataract') / 100) + '%'
        prediction.normal = str(res.get('normal') / 100) + '%'
        prediction.save()
        return jsonify(prediction.to_dict())


api.add_resource(Prediction, '/api/prediction')


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/predictions", methods=["GET"])
def prediction_list():
    return render_template("predictions.html")


if __name__ == "__main__":
    app.run(debug=True)
