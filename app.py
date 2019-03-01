# Micro gevent chatroom.
# ----------------------
# Make things as simple as possible, but not simpler.
from gevent.pywsgi import WSGIServer
from flask_cors import CORS, cross_origin
from flask import Flask, json, redirect, render_template, request
import tensorflow as tf
from gevent import monkey
monkey.patch_all()

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

app = Flask(__name__)
app.debug = True
CORS(app)

# Unpersists graph from file
with tf.gfile.FastGFile("retrained_graph.pb", "rb") as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name="")

# Loads label file, strips off carriage return
label_lines = [line.rstrip()
               for line in tf.gfile.GFile("retrained_labels.txt")]

# with tf.Session() as sess:
sess = tf.Session()


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_label(sess, image_data):
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name("final_result:0")

    predictions = sess.run(softmax_tensor,
                           {"DecodeJpeg/contents:0": image_data})

    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    result = {}

    for node_id in top_k:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        result[human_string] = int(round(float(score), 4) * 10000)
        print("%s (score = %.5f)" % (human_string, score))
    return result


@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            return redirect(request.url)
        if file and allowed_file(file.filename):
            msg = get_label(sess, file.read())
            msg["status"] = "success"
            msg["filename"] = file.filename
            tmp_cataract = msg["cataract"] / 100
            tmp_normal = msg["normal"] / 100
            if tmp_cataract >= 80:
                msg["advice"] = "小 Ai 提醒您，您的眼睛已经极可能患上白内障，请及时联系专业医师进行进一步的诊断！"
            elif tmp_cataract >= 60 and tmp_cataract < 80:
                msg["advice"] = "小 Ai 提醒您，您的眼睛极有可能正在被白内障侵扰，请及时联系专业医师进行进一步的诊断！"
            elif tmp_cataract >= 50 and tmp_cataract < 60:
                msg["advice"] = "小 Ai 稍微有点拿不准，但您的眼睛有很大的可能出现白内障，最好及时联系专业医师进行更精准地诊断！"
            elif tmp_cataract >= 40 and tmp_cataract < 50:
                msg["advice"] = "小 Ai 虽然不太确定，但您的眼睛出现了一些白内障才会有的症状，小 Ai 希望您能尽快寻求专业医师的帮助，进行专业的诊断！"
            elif tmp_cataract >= 20 and tmp_cataract < 40:
                msg["advice"] = "小 Ai 温馨提醒，您的眼睛基本没什么问题，出现白内障的可能较小，如果不放心，可向专业医师寻求诊断意见！"
            elif tmp_cataract >= 10 and tmp_cataract < 20:
                msg["advice"] = "小 Ai 基本能打包票，您的眼睛没有和白内障扯上任何关系，如果出了偏差，那就是机器开了小差！"
            elif tmp_cataract < 10:
                msg["advice"] = "小 Ai 极其肯定，您的眼睛非常健康，请注意继续保持用眼卫生哦！"
            msg["cataract"] = str(tmp_cataract) + "%"
            msg["normal"] = str(tmp_normal) + "%"
            return json.dumps(msg)
    return render_template("index.html")


if __name__ == "__main__":
    http = WSGIServer(("0.0.0.0", 5000), app)
    http.serve_forever()
