



















# | output: false
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import os

from IPython.display import Markdown

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    KFold,
)
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping












directory = "./Case-Study-6/data" if os.path.exists("./Case-Study-6/data") else "./data"
data = pd.read_csv(f"{directory}/all_train.csv")
data = data.rename(columns={"# label": "label"})

print(data)
print(data.dtypes)








# | label: fig-target-dist
# | fig-cap: "Distribution of Target Variable (Label). The classes are evenly distributed."
# print(data["label"].value_counts())

sns.set_theme(style="whitegrid")

# Plot the distribution of target variable (category)
# plt.figure(figsize=(8, 6))
sns.countplot(x="label", data=data, palette="viridis")
plt.title("Distribution of Target Variable")
plt.xlabel("Record Classification (signal or background)")
plt.ylabel("Count")
plt.show()





# | label: fig-mass-dist
# | fig-cap: "Distribution of Mass Variable. Mass appears to be uniformly distributed."

# plt.figure(figsize=(8, 6))
# sns.histplot(data["mass"], bins=5, kde=False, edgecolor="black")
plt.hist(data['mass'], bins=5, edgecolor='black')
plt.title("Histogram of Mass")
plt.xlabel("Mass")
plt.ylabel("Frequency")
plt.show()





# | label: fig-feature-dist
# | fig-cap: "Distribution of F4 Variable. This variable appears to be Uniformly distributed."

# plt.figure(figsize=(8, 6))
# sns.histplot(data["mass"], bins=5, kde=False, edgecolor="black")
plt.hist(data['f4'], bins=5, edgecolor='black')
plt.title("Histogram of 'f4' Variable")
plt.xlabel("f4")
plt.ylabel("Frequency")
plt.show()







# | output: false
# | eval: true
missing_by_column = data.isnull().sum()
total_missing = missing_by_column.sum()

missing_summary = pd.DataFrame(missing_by_column, columns=["Missing Values"])
missing_summary.loc["Total"] = total_missing

print(missing_summary)



# | label: tbl-missing-data
# | tbl-cap: "Missing data summary by attribute. There is no missing data in this dataset."

missing_md = missing_summary.to_markdown()
Markdown(missing_md)







scaler = StandardScaler()
y = data["label"]
X = data.drop(["label"], axis=1)
X = scaler.fit_transform(X)







# | output: false
# | eval: true

def build_model(input_shape):
    model = tf.keras.models.Sequential([
        # tf.keras.layers.Dense(256, activation='relu', input_shape=(input_shape,)),
        # tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


kf = KFold(n_splits=5, shuffle=True, random_state=42)
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=3, restore_best_weights=True
)

oof_preds = np.zeros(len(X))
oof_true = np.zeros(len(X))

# Lists to store the metrics for each fold
accuracy_list = []
precision_list = []
recall_list = []
f1_list = []

train_losses = []
val_losses = []

for train_index, val_index in kf.split(X):
    X_train, X_val = X[train_index], X[val_index]
    y_train, y_val = y[train_index], y[val_index]

    model = build_model(X_train.shape[1])
    history = model.fit(
        X_train,
        y_train,
        epochs=10,
        batch_size=64,
        verbose=1,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping],
    )

    # Append losses for each epoch
    train_losses.append(history.history['loss'])
    val_losses.append(history.history['val_loss'])

    y_pred = model.predict(X_val).flatten()

    # Store the predictions and true values
    oof_preds[val_index] = y_pred
    oof_true[val_index] = y_val

    # Convert probabilities to binary predictions
    y_pred_binary = (y_pred > 0.5).astype(int)

    # Calculate and store metrics for the current fold
    accuracy_list.append(accuracy_score(y_val, y_pred_binary))
    precision_list.append(precision_score(y_val, y_pred_binary))
    recall_list.append(recall_score(y_val, y_pred_binary))
    f1_list.append(f1_score(y_val, y_pred_binary))


# Convert from probabilities to binary predictions
oof_preds_binary = (oof_preds > 0.5).astype(int)

# Compute metrics for the entire dataset
accuracy = accuracy_score(oof_true, oof_preds_binary)
precision = precision_score(oof_true, oof_preds_binary)
recall = recall_score(oof_true, oof_preds_binary)
f1 = f1_score(oof_true, oof_preds_binary)

# Calculate mean and standard deviation of metrics for each fold
mean_accuracy = np.mean(accuracy_list)
std_accuracy = np.std(accuracy_list)
mean_precision = np.mean(precision_list)
std_precision = np.std(precision_list)
mean_recall = np.mean(recall_list)
std_recall = np.std(recall_list)
mean_f1 = np.mean(f1_list)
std_f1 = np.std(f1_list)



# | output: false
# | eval: false

# | label: fig-train-val-loss
# | fig-cap: "Training and Validation Losses per fold for each epoch in the Neural Network model."

# Plotting training and validation losses
fig, ax = plt.subplots()

colors_train = plt.cm.Blues(np.linspace(0.3, 0.7, len(train_losses)))
colors_val = plt.cm.Oranges(np.linspace(0.3, 0.7, len(val_losses)))

for i in range(len(train_losses)):
    ax.plot(train_losses[i], label=f'Train Fold {i+1}', color=colors_train[i], linestyle='-', marker='o')
    ax.plot(val_losses[i], label=f'Val Fold {i+1}', color=colors_val[i], linestyle='--', marker='x')

ax.set_title('Training and Validation Loss Per Epoch')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.legend()
plt.show()



# | output: true
# | eval: true

# | label: print-metrics-nn
print(f'Overall Accuracy: {accuracy}')
print(f'Overall Precision: {precision}')
print(f'Overall Recall: {recall}')
print(f'Overall F1 Score: {f1}')

print(f'Mean Accuracy: {mean_accuracy}, Std Accuracy: {std_accuracy}')
print(f'Mean Precision: {mean_precision}, Std Precision: {std_precision}')
print(f'Mean Recall: {mean_recall}, Std Recall: {std_recall}')
print(f'Mean F1 Score: {mean_f1}, Std F1 Score: {std_f1}')

# Optional print model info
print(model.summary())




# | output: false
# | eval: false

# | label: tbl-class-report-nn
# | tbl-cap: "Dense Neural Network Cross-Validation Classification Report"

class_report_dict = classification_report(oof_true, oof_preds_binary, output_dict=True)
class_report_df = pd.DataFrame(class_report_dict).transpose()
class_report_df.loc["accuracy"] = class_report_df.loc["accuracy"].drop(
    ["precision", "recall"]
)
class_report_df = class_report_df.rename(
    index={"0": "background", "1": "Signal"}
)
class_report_df = class_report_df.round(3)
class_report_df = class_report_df.fillna("")

metrics_md = class_report_df.to_markdown()
Markdown(metrics_md)







conf_matrix = confusion_matrix(y, oof_preds_binary)
class_report = classification_report(y, oof_preds_binary)
roc_auc = roc_auc_score(y, oof_preds)



# | label: fig-conf-matrix
# | fig-cap: "Dense NN Classifier Confusion Matrix. Out-of-fold predictions are used to evaluate the model."

# Plot confusion matrix with Seaborn
# plt.figure(figsize=(8, 6))
sns.heatmap(
    conf_matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Background", "Signal"],
    yticklabels=["Background", "Signal"],
)
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.show()


# | label: fig-roc-curve
# | fig-cap: "Dense NN Classifier ROC Curve. Out-of-fold predictions are used to evaluate the model."

# Plot ROC curve
fpr, tpr, _ = roc_curve(y, oof_preds)
# plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color="blue", lw=2, label=f"ROC curve (area = {roc_auc:.4f})")
plt.plot([0, 1], [0, 1], color="gray", lw=2, linestyle="--")
plt.xlim([-0.05, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.show()



# Display the classification report
print("\nClassification Report:")
print(class_report)
print(f"\nROC-AUC Score: {roc_auc:.4f}")



# | label: tbl-class-report
# | tbl-cap: "Dense NN Classification Report. The table shows the precision, recall, f1-score, and support for each class. Out-of-fold predictions are used to evaluate the model."

class_report_dict = classification_report(y, oof_preds_binary, output_dict=True)
class_report_df = pd.DataFrame(class_report_dict).transpose()
class_report_df.loc["accuracy"] = class_report_df.loc["accuracy"].drop(
    ["precision", "recall"]
)
class_report_df = class_report_df.rename(
    index={"0": "Background", "1": "Signal"}
)
class_report_df = class_report_df.round(3)
class_report_df = class_report_df.fillna("")

metrics_md = class_report_df.to_markdown()
Markdown(metrics_md)
