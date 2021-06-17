from __future__ import print_function
import sys
import psutil
from itertools import permutations
import timeit
from diceLibrary.logger import Logger
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def analytics():
    return render_template("index.html")

@app.route('/analyticsPage', methods = ['GET', 'POST'])
def analyticsPage():
    return render_template("index.html")

def main():
    app.run(host="0.0.0.0", port=8080)

if __name__ == '__main__':
    main()




