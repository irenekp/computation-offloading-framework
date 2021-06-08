from __future__ import print_function
import sys
import psutil
from itertools import permutations
import timeit
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/analytics', methods = ['GET', 'POST'])
def analytics():
    return render_template("index.html")

if __name__ == '__main__':
	app.run(host = "0.0.0.0", port=8080)




