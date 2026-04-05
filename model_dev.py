# Training script — run once locally to produce model.pt
# Requires: pip install scikit-learn torch
#
# The trained model is saved to model.pt and committed to the repo
# so it can be copied into the Docker image at build time.

import torch
import torch.nn as nn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from model import IrisNet


# dummy, normally some NN or RF from torch or scikit learn,
# ie. a model that can predict
class DummyModel:
    def predict(self, X):
        # Example: return the sum of each row
        return [sum(row) for row in X]

# model = DummyModel()
# predictions = model.predict([[11,22,33],[44,55,66],[77,88,99]])
# print(predictions)


# ── Data ─────────────────────────────────────────────────────────────────────
iris = load_iris()
X_all = torch.tensor(iris.data, dtype=torch.float32)
y_all = torch.tensor(iris.target, dtype=torch.long)

# Compute normalization stats from the full dataset
mean = X_all.mean(dim=0).tolist()
std  = X_all.std(dim=0).tolist()

X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
X_test  = torch.tensor(X_test,  dtype=torch.float32)
y_test  = torch.tensor(y_test,  dtype=torch.long)

# ── Model & training ──────────────────────────────────────────────────────────
model     = IrisNet(mean, std)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

for epoch in range(300):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train), y_train)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            acc = (model(X_test).argmax(1) == y_test).float().mean()
        print(f"Epoch {epoch+1:3d}  loss={loss.item():.4f}  test_acc={acc.item():.3f}")

# ── Save ──────────────────────────────────────────────────────────────────────
model.eval()
torch.save(model.state_dict(), "model.pt")
print("Saved model.pt")

# Quick sanity check
print("\nSample predictions (predicted class index):")
sample = torch.tensor([[5.1, 3.5, 1.4, 0.2],   # setosa     -> 0
                        [6.3, 3.3, 4.7, 1.6],   # versicolor -> 1
                        [6.3, 2.7, 4.9, 1.8]])  # virginica  -> 2
with torch.no_grad():
    preds = model(sample).argmax(1).tolist()
print(f"  {preds}  (expected [0, 1, 2])")
print(f"\nClass names: {list(iris.target_names)}")
