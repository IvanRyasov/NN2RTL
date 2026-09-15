import pickle
import onnx
from onnx import numpy_helper


def extract_sequential_layers(onnx_path: str):
    model = onnx.load(onnx_path)
    graph = model.graph

    # 1. Извлекаем все веса (константы) из модели в словарь {имя_тензора: numpy_массив}
    initializers = {
        init.name: numpy_helper.to_array(init) for init in graph.initializer
    }

    # 2. Собираем информацию о размерностях тензоров (для удобства)
    tensor_shapes = {}
    for vi in list(graph.input) + list(graph.output) + list(graph.value_info):
        shape = []
        for dim in vi.type.tensor_type.shape.dim:
            if dim.dim_value:
                shape.append(dim.dim_value)
            elif dim.dim_param:
                shape.append(dim.dim_param)
            else:
                shape.append(None)
        tensor_shapes[vi.name] = shape

    # 3. Проходим по нодам в порядке их топологического следования (выполнения)
    layers = []
    for idx, node in enumerate(graph.node):
        # Находим веса, которые принадлежат конкретно этому слою
        node_weights = {}
        for input_name in node.input:
            if input_name in initializers:
                node_weights[input_name] = initializers[input_name]

        # Собираем информацию о слое
        layer_data = {
            "index": idx,
            "name": node.name or f"{node.op_type}_{idx}",
            "op_type": node.op_type,
            "inputs": list(node.input),
            "outputs": list(node.output),
            "input_shapes": {
                inp: tensor_shapes.get(inp) for inp in node.input if inp
            },
            "output_shapes": {
                out: tensor_shapes.get(out) for out in node.output if out
            },
            "weights": node_weights,  # Словарь {имя_веса: numpy_array}
        }
        layers.append(layer_data)

    return layers


if __name__ == "__main__":
    onnx_model_path = "exampleModel.onnx"  # Укажите путь к вашему файлу
    output_pickle_path = "layers_with_weights.pkl"

    print("Извлечение слоев...")
    sequential_layers = extract_sequential_layers(onnx_model_path)

    # Сохраняем полученный массив в файл pkl
    print(f"Сохранение в файл {output_pickle_path}...")
    with open(output_pickle_path, "wb") as f:
        pickle.dump(sequential_layers, f)

    print("Готово!")

    # --- Демонстрация того, как прочитать этот файл и посмотреть веса ---
    print("\n--- Пример чтения сохраненных данных ---")
    with open(output_pickle_path, "rb") as f:
        loaded_layers = pickle.load(f)

    # Выведем первые 5 слоев для теста
    for layer in loaded_layers[:5]:
        print(
            f"Слой [{layer['index']}]: {layer['name']} (Тип: {layer['op_type']})"
        )
        if layer["weights"]:
            print("  Веса этого слоя:")
            for weight_name, weight_array in layer["weights"].items():
                print(
                    f"    - {weight_name}: shape={weight_array.shape}, dtype={weight_array.dtype}"
                )
        else:
            print("  (Нет весов / просто активация)")