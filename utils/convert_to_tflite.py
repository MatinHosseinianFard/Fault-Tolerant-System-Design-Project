import tensorflow as tf
import numpy as np
from tqdm import tqdm

def representative_dataset_generator():
        """
        Creates a representative dataset for TFLite model quantization.

        This function generates batches of data from the training or testing dataset
        to help TFLite model quantization process understand the input distribution.

        Yields:
            A single batch of input data for the model (as a numpy array).
        """
        X_test = np.load('./npy_files/X_test.npy')
        for i in tqdm(range(len(X_test))):
            # Use only one sample at a time, as required by TFLite quantization
            sample = X_test[i:i+1].astype(np.float32)
            yield [sample]

code_path = "./code/results/epochs100_pat10_val0.25"

# Load the saved Keras model from .h5 file
model_path = f"{code_path}/PCnnLstm_checkpoint.keras"  # Replace with the path to your .h5 model
model = tf.keras.models.load_model(model_path)

# Pass this function to the TFLite converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset_generator

# Specify the input and output types as int8
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
converter.target_spec.supported_types = [tf.int8]

tflite_model = converter.convert()

with open(f"{code_path}/model.tflite", "wb") as f:
    f.write(tflite_model)

    # Load the TFLite model
tflite_model_path = f"{code_path}/model.tflite"
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)

# Allocate tensors
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("=== Input Details ===")
for i, detail in enumerate(input_details):
    print(f"Input {i}:")
    print(f"  Name: {detail['name']}")
    print(f"  Shape: {detail['shape']}")
    print(f"  Data Type: {detail['dtype']}")

print("\n=== Output Details ===")
for i, detail in enumerate(output_details):
    print(f"Output {i}:")
    print(f"  Name: {detail['name']}")
    print(f"  Shape: {detail['shape']}")
    print(f"  Data Type: {detail['dtype']}")

# Get all layer details (Optional)
print("\n=== Tensor Details ===")
for tensor in interpreter.get_tensor_details():
    print(f"Tensor Name: {tensor['name']}")
    print(f"  Index: {tensor['index']}")
    print(f"  Shape: {tensor['shape']}")
    print(f"  Data Type: {tensor['dtype']}")
    print()

tensor_details = interpreter.get_tensor_details()
total_memory = 0

for tensor in tensor_details:
    tensor_shape = tensor['shape']
    tensor_type = tensor['dtype']
    tensor_size = tf.dtypes.as_dtype(tensor_type).size * tf.reduce_prod(tensor_shape)
    total_memory += tensor_size.numpy()

print(f"Total Memory Required: {total_memory} bytes")