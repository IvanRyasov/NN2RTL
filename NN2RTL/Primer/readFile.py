import pickle

# Открываем файл в бинарном режиме чтения ('rb')
with open('layers_with_weights.pkl', 'rb') as f:
    data = pickle.load(f)

print(data)
