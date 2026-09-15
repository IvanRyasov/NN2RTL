import numpy as np
import tensorflow as tf
import tf2onnx
import onnx
from onnx import numpy_helper
import onnxruntime as ort

KERAS_PATH = "e.keras"
ONNX_PATH = "exampleModel.onnx"

# ---------- 1. Загружаем модель ----------
keras_model = tf.keras.models.load_model(KERAS_PATH)
keras_model.summary()

# ---------- 2. Конвертируем через tf.function ----------
input_shape = keras_model.inputs[0].shape          # например (None, 28, 28, 1)
spec = (tf.TensorSpec(input_shape, tf.float32, name="input"),)

@tf.function(input_signature=spec)
def model_fn(x):
    return keras_model(x, training=False)

onnx_model, _ = tf2onnx.convert.from_function(
    model_fn,
    input_signature=spec,
    opset=13,
    output_path=ONNX_PATH,
)
print(f"Сохранено: {ONNX_PATH}")

# ---------- 3. Читаем параметры через onnx ----------
model = onnx.load(ONNX_PATH)
onnx.checker.check_model(model)

params = {}
for init in model.graph.initializer:
    arr = numpy_helper.to_array(init)
    params[init.name] = arr
    print(f"{init.name:60s} {arr.shape} {arr.dtype}")

print("Всего параметров:", sum(p.size for p in params.values()))

# ---------- 4. Инференс через onnxruntime ----------
sess = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
inp = sess.get_inputs()[0].name
out = sess.get_outputs()[0].name

test_shape = [1 if d is None else d for d in input_shape]
x = np.random.rand(*test_shape).astype(np.float32)

onnx_out = sess.run([out], {inp: x})[0]
keras_out = keras_model.predict(x, verbose=0)
print("Макс. расхождение:", np.abs(onnx_out - keras_out).max())