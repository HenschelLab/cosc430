from flask import Flask, request, jsonify

app = Flask(__name__)

# dummy, normally some NN or RF from torch or scikit learn, 
# ie. a model that can predict
class DummyModel:
    def predict(self, X):
        # Example: return the sum of each row
        return [sum(row) for row in X]

MODEL = DummyModel()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    X = data["X"]
    y = MODEL.predict(X)
    return jsonify({"y": y}), 200

@app.route("/")
def home():
    return "Im in the middle of a lecture"

if __name__ == "__main__":
    app.run(debug=True)


'''
Quick command line test:

curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"X": [[41, 2, 3], [10, 20, 30]]}'


{
  "y": [
    46,
    60
  ]
}
'''
