TUDA – Python Email Forensics Agent
Overview

TUDA (Tightening Up Data Analytics) is a Python‑based email‑forensics agent designed to fetch, parse and analyze metadata from Gmail messages.
The core features include:

Command‑line daemon – runs as a background service that reads Gmail messages and stores metadata in an encrypted SQLite database.

Optional Flask UI – a lightweight web interface to browse messages, metadata and additional analytics.

Plug‑in architecture – allows third‑party modules to add analytics tasks such as spam detection or named‑entity recognition.

This codebase is not an Android application; it is intended for deployment on desktop or server environments.
See the repository's quantized_models.md for recommended machine‑learning models.

Project plan

Repository clean‑up and organization
Document each module (daemon, email parsing, intel tagging, web UI, plug‑ins) and adopt Python packaging conventions (pyproject.toml).
Simplify the folder structure, and add meaningful docstrings and type hints.

Testing and continuous integration
Write unit tests for metadata extraction, NLP functions and plug‑ins.
Configure GitHub Actions to run linting (ruff, black) and test suites on each commit.

Security and privacy
Since TUDA processes email metadata, enforce strict data handling and encryption.
Use AES‑encrypted SQLite databases; handle OAuth tokens securely; implement configurable retention policies to minimize data storage.

Packaging and distribution
Provide installation via pip and packaged distribution using PyInstaller for desktop use.
Offer a Dockerfile for containerized deployment.

Integration of quantized models
Use quantized Transformer models to add efficient spam detection and named‑entity extraction:

The AventIQ‑AI/bert‑spam‑detection model is a quantized BERT fine‑tuned for email spam detection. It offers high precision, recall and F1‑score (~0.99) while using int8 weights and activations.

The Zefty/distilbert‑ner‑email‑org model is a distilled BERT that identifies organization entities in job‑application emails.

Quantization reduces memory and computational requirements by representing neural network weights and activations with lower precision (e.g., 8‑bit). TUDA can integrate quantized models using the transformers and bitsandbytes libraries.
Implement plug‑ins that load these models for classification and entity recognition tasks within the daemon and UI.

Future work
Add a REST API to expose metadata and analytics results.
Explore additional quantized models for phishing detection and sentiment analysis.
Consider ethical monetization options, such as premium features for advanced analytics.

Getting started

Clone the repo and install dependencies:

git clone https://github.com/malik-io/tuda.git
cd tuda
pip install -r requirements.txt


Obtain Gmail OAuth credentials and run the daemon:

python main.py --config tuda.conf


Access the optional Flask UI at http://localhost:5000/.

Quantized Models for TUDA

TUDA uses quantized Transformer models to perform email analytics efficiently. Quantization involves representing model weights and activations with lower precision (8‑bit or 4‑bit) to reduce memory footprint and computational cost while preserving accuracy.

Task	Model	Description	Metrics
Spam detection	AventIQ‑AI/bert‑spam‑detection	Quantized BERT‑base model fine‑tuned to classify email text as spam or not. Achieves precision ≈0.99, recall ≈0.99 and F1‑score ≈0.99.	Precision ≈0.99, recall ≈0.99, F1 ≈0.99
Organization entity recognition	Zefty/distilbert‑ner‑email‑org	DistilBERT model fine‑tuned to recognize only organization entities in job‑application emails. Suitable for retrieving company names from messages.	Accuracy not published; model specialized for ORG entities only
Integration

These models can be loaded using the Hugging Face transformers library. For quantized inference, set load_in_8bit=True (or load_in_4bit=True) to leverage the bitsandbytes integration. Example:

from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained(
    "AventIQ-AI/bert-spam-detection",
    load_in_8bit=True,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("AventIQ-AI/bert-spam-detection")

text = "Congratulations! You've won a prize. Click here to claim."
inputs = tokenizer(text, return_tensors="pt")
logits = model(**inputs).logits
pred = logits.softmax(dim=-1).argmax().item()

if pred == 1:
    print("Spam")
else:
    print("Not spam")


Similarly, load the NER model with AutoModelForTokenClassification to recognize organization entities. Integrate these models as TUDA plug‑ins for classification and entity extraction within the daemon and UI.

The repository is undergoing reorganization. For information on the quantized models used in TUDA, see quantized_models.md.
