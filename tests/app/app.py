from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/html/')
def html():
    return render_template('form.html')


@app.route('/form/', methods=['POST'])
def form():
    return render_template('data.html', value=request.form['field'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
