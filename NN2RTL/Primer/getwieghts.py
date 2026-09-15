import onnx

onnx_model = onnx.load("exampleModel.onnx")

for initializer in onnx_model.graph.initializer:
    weights = onnx.numpy_helper.to_array(initializer)

    print(
        f"Имя: {initializer.name}, "
        f"форма: {weights.shape}, "
        f"dtype: {weights.dtype}"
    )