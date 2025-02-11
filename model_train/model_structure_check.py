from safetensors import safe_open
from transformers import AutoModel

if True:
    with safe_open("afsim_3b_bp16.safetensors", framework="pt") as f:
        for tensor_name in f.keys():
            tensor = f.get_tensor(tensor_name)
            print(f"Tensor: {tensor_name}")
            print(f"Data type: {tensor.dtype}")

else:
    # 加载模型
    model = AutoModel.from_pretrained("/data/Large-Model/Qwen/Qwen2___5-Coder-3B-Instruct/")

    # 打印模型结构
    print(model)

    # 分析模型参数
    with open("qwen2.5-coder-3b-model_parameters.txt", "w") as f:
        for name, param in model.named_parameters():
            f.write(f"Layer: {name}\n")
            f.write(f"Shape: {param.shape}\n")
            f.write(f"Dtype: {param.dtype}\n")
            f.write(f"Number of parameters: {param.numel()}\n")
            f.write("---\n")

    # 加载模型
    model = AutoModel.from_pretrained("/home/ubuntu/ycd/cpt-models/Qwen2.5-Coder-3B-Instruct/full/train_2025-01-07-21-03-26/")

    # 打印模型结构
    print(model)

    # 分析模型参数
    with open("afsim-3b-model_parameters.txt", "w") as f:
        for name, param in model.named_parameters():
            f.write(f"Layer: {name}\n")
            f.write(f"Shape: {param.shape}\n")
            f.write(f"Dtype: {param.dtype}\n")
            f.write(f"Number of parameters: {param.numel()}\n")
            f.write("---\n")
