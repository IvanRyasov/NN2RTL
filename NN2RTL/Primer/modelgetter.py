import onnxruntime as ort
import onnx
from onnx import numpy_helper

session = ort.InferenceSession(
    "exampleModel.onnx",
    providers=["CPUExecutionProvider"]
)

# Информация о входах и выходах
for input_info in session.get_inputs():
    print("Вход:")
    print("  name:", input_info.name)
    print("  shape:", input_info.shape)
    print("  type:", input_info.type)

for output_info in session.get_outputs():
    print("Выход:")
    print("  name:", output_info.name)
    print("  shape:", output_info.shape)
    print("  type:", output_info.type)

onnx_model = onnx.load("exampleModel.onnx")

parameters = {
    initializer.name: numpy_helper.to_array(initializer)
    for initializer in onnx_model.graph.initializer
}

print(parameters.keys())