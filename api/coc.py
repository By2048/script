import time
from pathlib import WindowsPath

import easyocr
from flask import Flask, jsonify

app = Flask(__name__)

reader = easyocr.Reader(
    lang_list=['en'],
    model_storage_directory=r"E:\Download\EasyORC",
    download_enabled=False
)


@app.route('/coc/<string:image>')
def coc(image):
    result = {"time": 0, "data": [0, 0, 0]}

    if not image:
        return jsonify(result)

    image = WindowsPath(image)
    if not image.exists():
        return jsonify(result)

    _start = time.time()
    orc = reader.readtext(image=str(image), allowlist="0123456789")
    _end = time.time()

    _time = _end - _start
    _time = round(_time, 2)

    if len(orc) != 3:
        result['data'] = [0, 0, 0]
        return jsonify(result)

    a, b, c = orc
    a, b, c = a[1], b[1], c[1]
    a, b, c = int(a), int(b), int(c)

    result["time"] = _time
    result["data"] = [a, b, c]
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=1331, debug=True)
