import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import ks_2samp

from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# =========================================================
# Загрузка данных
# =========================================================

wine = load_wine(as_frame=True)

X = wine.data.copy()
y = wine.target.copy()

# =========================================================
# Train / Reference split
# =========================================================

X_train, X_reference, y_train, y_reference = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# =========================================================
# Обучение модели
# =========================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# =========================================================
# Reference quality
# =========================================================

y_pred_reference = model.predict(X_reference)

reference_accuracy = accuracy_score(
    y_reference,
    y_pred_reference
)

# =========================================================
# Создание current batch с drift
# =========================================================

X_current = X_reference.copy()

X_current["alcohol"] *= 1.5
X_current["malic_acid"] *= 2.0
X_current["color_intensity"] += 5
X_current["proline"] += 700

# =========================================================
# Current quality
# =========================================================

y_pred_current = model.predict(X_current)

current_accuracy = accuracy_score(
    y_reference,
    y_pred_current
)

accuracy_drop = reference_accuracy - current_accuracy

# =========================================================
# Drift analysis
# =========================================================

drift_results = []

for col in X_reference.columns:

    stat, p_value = ks_2samp(
        X_reference[col],
        X_current[col]
    )

    drift_results.append({
        "Признак": col,
        "Mean Reference": round(X_reference[col].mean(), 2),
        "Mean Current": round(X_current[col].mean(), 2),
        "KS Statistic": round(stat, 4),
        "p-value": round(p_value, 6),
        "Drift Detected": "YES" if p_value < 0.05 else "NO"
    })

drift_df = pd.DataFrame(drift_results)

# =========================================================
# Summary
# =========================================================

print("=" * 70)
print("           MODEL DRIFT & DEGRADATION REPORT")
print("=" * 70)

print("\n[1] MODEL QUALITY")

print(f"""
Reference Accuracy : {reference_accuracy:.4f}
Current Accuracy   : {current_accuracy:.4f}
Accuracy Drop      : {accuracy_drop:.4f}
""")

print("-" * 70)

print("\n[2] DATA DRIFT ANALYSIS")

display(drift_df)

print("-" * 70)

print("\n[3] CLASSIFICATION REPORT")

print(
    classification_report(
        y_reference,
        y_pred_current,
        zero_division=0
    )
)

# =========================================================
# Accuracy comparison chart
# =========================================================

plt.figure(figsize=(6, 4))

bars = plt.bar(
    ["Reference", "Current"],
    [reference_accuracy, current_accuracy]
)

plt.ylabel("Accuracy")
plt.title("Model Accuracy Degradation")

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 0.01,
        f"{height:.3f}",
        ha='center',
        fontsize=11
    )

plt.ylim(0, 1.1)

plt.show()

# =========================================================
# Distribution comparison
# =========================================================

selected_columns = [
    "alcohol",
    "malic_acid",
    "color_intensity",
    "proline"
]

russian_titles = {
    "alcohol": "Alcohol",
    "malic_acid": "Malic Acid",
    "color_intensity": "Color Intensity",
    "proline": "Proline"
}

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 10)
)

axes = axes.ravel()

for i, col in enumerate(selected_columns):

    # Reference batch
    axes[i].hist(
        X_reference[col],
        bins=20,
        alpha=0.65,
        density=True,
        label="Reference",
        color="red",
        edgecolor="black"
    )

    # Current batch
    axes[i].hist(
        X_current[col],
        bins=20,
        alpha=0.65,
        density=True,
        label="Current",
        color="green",
        edgecolor="black"
    )

    axes[i].set_title(
        russian_titles[col],
        fontsize=12,
        fontweight='bold'
    )

    axes[i].set_xlabel("Value")

    axes[i].set_ylabel("Density")

    axes[i].legend()

    axes[i].grid(alpha=0.3)

plt.suptitle(
    "Feature Distribution Drift",
    fontsize=16,
    fontweight='bold'
)

plt.tight_layout()

plt.show()
# =========================================================
# Boxplots
# =========================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 10)
)

axes = axes.ravel()

for i, col in enumerate(selected_columns):

    axes[i].boxplot(
        [
            X_reference[col],
            X_current[col]
        ],
        labels=["Reference", "Current"]
    )

    axes[i].set_title(
        russian_titles[col],
        fontsize=12,
        fontweight='bold'
    )

    axes[i].grid(alpha=0.3)

plt.suptitle(
    "Boxplot Comparison: Reference vs Current",
    fontsize=16,
    fontweight='bold'
)

plt.tight_layout()

plt.show()