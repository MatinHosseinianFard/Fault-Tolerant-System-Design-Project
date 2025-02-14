# Improving Battery Thermal Management Using a Model-Based Virtual Temperature Sensor

## Overview

This repository contains the implementation of a **PCNN-LSTM** model for virtual temperature sensing of lithium-ion batteries. The model is trained using the **NASA battery dataset** and deployed on an **ESP32-S3 microcontroller** after post-training quantization (PTQ). The primary goal of this work is to optimize battery thermal management by predicting battery surface temperature using **voltage and current** readings.

## Features

- **Hybrid PCNN-LSTM Model**: Combines **CNN** for feature extraction and **LSTM** for sequential modeling.
- **Dataset Handling**: Processes **NASA battery dataset** for training and testing.
- **Quantization for Edge Deployment**: Applies **full integer (INT8) quantization** for microcontroller execution.
- **Deployment on ESP32-S3**:
  - **Memory-efficient model conversion** using TensorFlow Lite.
  - **Integration with microcontroller hardware** for real-time inference.
- **Comparison Metrics**:
  - **Mean Absolute Error (MAE)**
  - **Root Mean Squared Error (RMSE)**
  - Evaluation of quantization impact on accuracy.

---

## Implementation Details

### Dataset

- **Source**: [NASA Battery Aging Dataset](https://www.nasa.gov)
- **Selected Batteries**:
  - **Training:** Batteries 30, 31, 32
  - **Testing:** Battery 29
- **Features Used**:
  - Measured voltage
  - Measured current
  - Measured temperature
  - Computed mean voltage and current
  - Integrated current over time

### Data Preprocessing

1. **MATLAB to CSV Conversion**:
   - Extracts raw **MATLAB** (.mat) files.
   - Converts necessary features into **CSV** format.
2. **Data Cleaning & Normalization**:
   - Standardized using **Z-score normalization**:
     \[
     X_{\text{norm}} = \frac{X - \mu}{\sigma}
     \]
   - Missing values handled and sequences generated for time-series modeling.
3. **Dataset Preparation**:
   - Concatenation of relevant charge/discharge cycles.
   - Removal of impedance measurement cycles.
   - Saving processed data in `.npy` format for efficient model training.

---

## Model Architecture

The **PCNN-LSTM** model follows this structure:

1. **1D Convolutional Layer (CNN)**:
   - Extracts local features from the time-series input.
2. **LSTM Layers**:
   - Captures temporal dependencies in battery signals.
3. **Fully Connected Layers**:
   - Outputs predicted battery surface temperature.

---

## Training Process

- **Framework**: TensorFlow 2.18.0
- **Batch Size**: 32
- **Epochs Tested**: 10, 20, 30, 40
- **Optimizer**: Adam
- **Loss Function**: Mean Squared Error (MSE)
- **Early Stopping**: Applied for optimal convergence

---

## Quantization & Edge Deployment

### **1. TensorFlow Lite Conversion**
- Model converted from **.keras** format to **TensorFlow Lite (.tflite)**.
- Applied **full integer quantization (INT8)** for edge efficiency.

### **2. Model Deployment on ESP32-S3**
- **Board Used**: ESP32-S3-N16R8
- **Specifications**:
  - **Flash Memory**: 16 MB
  - **RAM**: 512 KB (SRAM) + 16 MB (PSRAM)
  - **Clock Speed**: 240 MHz
- **Conversion to C Format**:
  - **`xxd` tool** used to convert `.tflite` to **C array** (`model.h`).
  - Model stored in **Flash Memory (PROGMEM)** to optimize RAM usage.
- **Integration with Arduino IDE**:
  - Used **EdgeNeuron** library for inference on ESP32.

---

## Performance Evaluation

### **Error Metrics (Before & After Quantization)**

| Epochs | Model          | MAE (°C) | RMSE (°C) |
|--------|---------------|----------|-----------|
| 10     | TensorFlow    | 0.64     | 1.61      |
|        | TFLite on ESP | 0.78     | 1.08      |
| 20     | TensorFlow    | 1.60     | 2.61      |
|        | TFLite on ESP | 0.63     | 0.94      |
| 30     | TensorFlow    | 1.43     | 2.91      |
|        | TFLite on ESP | 2.73     | 3.43      |
| 40     | TensorFlow    | 1.42     | 2.49      |
|        | TFLite on ESP | 0.79     | 1.41      |

- **Key Findings**:
  - Quantization **improves accuracy in some cases** due to implicit regularization.
  - **Reduced RMSE** in epochs **10, 20, and 40**, showing better generalization.
  - Some accuracy loss at **30 epochs**, indicating dependency on training dynamics.

---


