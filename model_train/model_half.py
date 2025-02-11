import safetensors.torch
import torch
from transformers import AutoTokenizer, Qwen2ForCausalLM

path = "/home/ubuntu/ycd/cpt-models/Qwen2.5-Coder-3B-Instruct/full/train_2025-01-07-21-03-26/"
model = Qwen2ForCausalLM.from_pretrained(path)
tokenizer = AutoTokenizer.from_pretrained(path)

if True:
    model = model.to(dtype=torch.bfloat16)
    model.save_pretrained(
        "afsim_3b_bf16",
        # torch_dtype=torch.bfloat16  # 或 torch.float16
    )
    tokenizer.save_pretrained("afsim_3b_bf16")
elif False:
    model = model.to(dtype=torch.bfloat16)
    safetensors.torch.save_file(model.state_dict(), 'afsim_3b_bf16.safetensors')
else:
    model = model.half()
    safetensors.torch.save_file(model.state_dict(), 'afsim_3b_fp16.safetensors')

