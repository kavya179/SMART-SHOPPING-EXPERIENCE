"""
Training and Evaluation Script for Joyory SmartMatch FAQ Intent Classifier & Semantic Index.

Architecture:
- TF-IDF N-Gram Vectorizer + Logistic Regression Classifier (Lightweight, CPU-friendly)
- Semantic Question-Answer Retrieval with Cosine Similarity
- Serializes trained artifacts to `backend/products/ml_models/`
"""

import os
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score


CURATED_FAQ_KNOWLEDGE_BASE = [
    {
        "id": "faq_smartmatch_quiz",
        "question": "How does the Joyory SmartMatch recommendation quiz work?",
        "variants": [
            "How does SmartMatch algorithm work?",
            "How do you recommend products?",
            "What is the logic behind recommendation score?",
            "How are personalized matches calculated?"
        ],
        "intent": "platform_policy",
        "answer": "Joyory SmartMatch uses a deterministic rule-based matching engine. It evaluates your selected category, skin type compatibility, target concerns, preferred active ingredients, and budget against verified product attributes to calculate a percentage match score."
    },
    {
        "id": "faq_authenticity",
        "question": "Are products listed in the catalog genuine and authentic?",
        "variants": [
            "Are these real products or fake?",
            "Is the formulation authentic?",
            "Are brand specifications verified?"
        ],
        "intent": "platform_policy",
        "answer": "All products listed in the Joyory SmartMatch catalog feature verified specifications, genuine brand formulations, and transparent INCI ingredient listings."
    },
    {
        "id": "faq_shipping_delivery",
        "question": "What is your shipping policy and delivery time?",
        "variants": [
            "How much is shipping fee?",
            "What is the delivery charge?",
            "When will my order arrive?",
            "Do you offer free delivery?"
        ],
        "intent": "platform_policy",
        "answer": "Standard shipping is FREE on all orders above ₹499. For orders below ₹499, a flat shipping fee of ₹50 applies. Estimated delivery time is 2–3 business days."
    },
    {
        "id": "faq_payment_checkout",
        "question": "What payment methods are supported on the platform?",
        "variants": [
            "Can I pay with cash on delivery?",
            "Do you accept credit cards or net banking?",
            "How does demo checkout work?"
        ],
        "intent": "platform_policy",
        "answer": "Joyory SmartMatch is a hackathon prototype with a safe, simulated demo checkout. We support demo Cash on Delivery and simulated Net Banking. No real money or credit card details are processed."
    },
    {
        "id": "faq_patch_test_guide",
        "question": "How do I perform a patch test for safe cosmetic use?",
        "variants": [
            "What are the steps to patch test a new serum?",
            "How to test for skin allergy before use?",
            "Where should I test a new skincare product?"
        ],
        "intent": "safety_and_cautions",
        "answer": "To perform a patch test: Apply 2–3 drops of the formula to a small area of clean skin on your inner forearm. Leave it for 24 hours. If no redness, burning, or itching occurs, the product is generally suitable for regular facial application."
    },
    {
        "id": "faq_returns_refunds",
        "question": "What is the return and refund policy for products?",
        "variants": [
            "Can I return an opened product?",
            "How do refunds work in the demo?",
            "What if I receive a damaged product?"
        ],
        "intent": "platform_policy",
        "answer": "Unopened products in original packaging can be returned within 14 days of delivery. For demo orders, returns and simulated refunds are handled through customer support."
    }
]


def train_and_save_faq_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'faq_intent_dataset.json')
    models_dir = os.path.join(base_dir, 'ml_models')
    os.makedirs(models_dir, exist_ok=True)

    print("=" * 65)
    print("Joyory SmartMatch — FAQ Intent Model & Semantic Index Training")
    print("=" * 65)

    # 1. Load Intent Dataset
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    samples = dataset['data']
    texts = [s['text'] for s in samples]
    labels = [s['intent'] for s in samples]

    print(f"Loaded {len(texts)} training samples across {len(set(labels))} distinct intents:")
    for intent in sorted(set(labels)):
        count = labels.count(intent)
        print(f"  - {intent:<28}: {count:>2} samples")

    # 2. Stratified Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    # 3. Build & Train Classification Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, sublinear_tf=True, lowercase=True)),
        ('clf', LogisticRegression(C=1.5, max_iter=300, class_weight='balanced', random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    # 4. Evaluate Classifier
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print("\n--- Evaluation on Held-Out Test Set (25% split) ---")
    print(f"Accuracy: {acc * 100:.2f}% | Weighted F1 Score: {f1 * 100:.2f}%")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # 5. Fit full dataset for deployment artifact
    full_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, sublinear_tf=True, lowercase=True)),
        ('clf', LogisticRegression(C=1.5, max_iter=300, class_weight='balanced', random_state=42))
    ])
    full_pipeline.fit(texts, labels)

    classifier_save_path = os.path.join(models_dir, 'faq_intent_classifier.joblib')
    joblib.dump(full_pipeline, classifier_save_path)
    print(f"\nSaved trained intent classifier to:\n  -> {classifier_save_path}")

    # 6. Build Semantic Question-Answer Retrieval Index
    qa_texts = []
    qa_records = []
    for item in CURATED_FAQ_KNOWLEDGE_BASE:
        qa_texts.append(item['question'])
        qa_records.append(item)
        for variant in item.get('variants', []):
            qa_texts.append(variant)
            qa_records.append(item)

    semantic_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True)
    semantic_matrix = semantic_vectorizer.fit_transform(qa_texts)

    semantic_bundle = {
        'vectorizer': semantic_vectorizer,
        'tfidf_matrix': semantic_matrix,
        'records': qa_records,
        'knowledge_base': CURATED_FAQ_KNOWLEDGE_BASE
    }

    retrieval_save_path = os.path.join(models_dir, 'faq_semantic_index.joblib')
    joblib.dump(semantic_bundle, retrieval_save_path)
    print(f"Saved semantic QA retrieval index to:\n  -> {retrieval_save_path}")

    print("\nModel training & indexing complete!")


if __name__ == '__main__':
    train_and_save_faq_models()
