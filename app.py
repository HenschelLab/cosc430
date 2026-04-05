import torch
from flask import Flask, request, jsonify

from model import IrisNet

app = Flask(__name__)

# Load trained IrisNet from saved state dict
_checkpoint = torch.load("model.pt", map_location="cpu", weights_only=True)
# mean and std are stored as buffers inside the checkpoint
_mean = _checkpoint["mean"].tolist()
_std  = _checkpoint["std"].tolist()
MODEL = IrisNet(_mean, _std)
MODEL.load_state_dict(_checkpoint)
MODEL.eval()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    X = torch.tensor(data["X"], dtype=torch.float32)
    with torch.no_grad():
        y = MODEL(X).argmax(dim=1).tolist()
    return jsonify({"y": y}), 200

@app.route("/")
def home():
    return "Im in the middle of a lecture again"

if __name__ == "__main__":
    app.run(debug=True)


'''
Quick command line test (Iris: 4 features per row, returns class index 0/1/2):

curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"X": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6], [6.3, 2.7, 4.9, 1.8]]}'

{
  "y": [0, 1, 2]
}
'''
