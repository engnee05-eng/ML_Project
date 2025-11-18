import torch
from torch.utils.data import DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datasets import Dataset
import pandas as pd
import os

# ---------------- LOAD DATA ----------------
df = pd.read_csv("dataset.csv").rename(columns={"Garhwali": "src", "Hindi": "tgt"})
df = df.dropna(subset=["src", "tgt"])  # remove empty rows
df["src"] = df["src"].astype(str)
df["tgt"] = df["tgt"].astype(str)
dataset = Dataset.from_pandas(df)
print(dataset)
# ---------------- LOAD TOKENIZER & MODEL ----------------
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
print(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
print(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

print("✅ Data and model loaded")

# ---------------- PREPROCESS ----------------
def encode(batch):
    print("Encoding batch...")  # debug
    inputs = tokenizer(
        ["translate Garhwali to Hindi: " + text for text in batch["src"]],
        max_length=32, truncation=True, padding="max_length"
    )
    labels = tokenizer(
        batch["tgt"],
        max_length=32, truncation=True, padding="max_length"
    )
    inputs["labels"] = labels["input_ids"]
    return inputs

dataset = dataset.map(encode, batched=True)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
loader = DataLoader(dataset, batch_size=1, shuffle=True)

print("✅ Preprocessing complete")

# ---------------- TRAIN ----------------
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
EPOCHS = 1

print("🔥 Training started...")
for epoch in range(EPOCHS):
    total_loss = 0
    for i, batch in enumerate(loader):
        batch = {k: v.to(device) for k, v in batch.items()}
        optimizer.zero_grad()
        loss = model(**batch).loss
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

        print(f"Batch {i+1}/{len(loader)} — Loss: {loss.item():.4f}")

    print(f"Epoch {epoch+1}/{EPOCHS} — Total Loss: {total_loss:.4f}")
print("✅ Training complete!")

# ---------------- SAVE MODEL ----------------
os.makedirs("model_out", exist_ok=True)
model.save_pretrained("model_out")
tokenizer.save_pretrained("model_out")
print("🎉 Model saved in model_out/")