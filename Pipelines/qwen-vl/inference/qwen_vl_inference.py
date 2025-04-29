# %% [markdown]
# ### Qwen-VL Inference Pipeline

# %% [markdown]
# ##### Imports
# 

# %%
import gc
import os
import re
import torch
import warnings
import transformers
from PIL import Image

# %% [markdown]
# ##### Disabling Warnings
# 

# %%
warnings.filterwarnings("ignore")

# %% [markdown]
# ##### Setting Training Device
# 

# %%
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if str(device) == "cuda":
    print(f"Using GPU {torch.cuda.get_device_properties(device)}")
else:
    print("Using CPU")

# %% [markdown]
# ##### Emptying the GPU Cache (if necessary)
# 

# %%
def empty_cache() -> None:
    # Cleaning out the device cache
    gc.collect()
    torch.cuda.empty_cache()


def print_free_memory() -> None:
    free, total = torch.cuda.mem_get_info(device)
    print(f"Percent of free memory: {round(free/total *100,2)}")


empty_cache()
print_free_memory()

# %% [markdown]
# ##### Memory Summary
# 

# %%
def memory_summary() -> None:
    print(torch.cuda.memory_summary())


memory_summary()

# %% [markdown]
# ##### Preparing GPU (if necessary)
# 

# %%
# For AMD GPU - 7800xt
device_name = torch.cuda.get_device_name(0)
if "AMD" in device_name or "Radeon" in device_name:
    os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

print(f"GPU {torch.cuda.get_device_properties(device).name} is now setup")

# %% [markdown]
# #####
# 

# %% [markdown]
# ##### Setting Flexible Paths for Data and Base Model
# 

# %%
# Directory Paths
training_dataset_name = "coco8"
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)
test_image_path = f"Weird-Stuff-In-Traffic/Data/yolo/{training_dataset_name}/images/train/000000000025.jpg"
complete_test_image_data_path = path_to_base_directory + test_image_path

# Model Paths
base_model_name = "Qwen/Qwen2-VL-2B-Instruct-AWQ"

# %% [markdown]
# ##### Preparing Processor

# %%
# Initialize Processor
processor = transformers.Qwen2VLProcessor.from_pretrained(base_model_name)

# %% [markdown]
# ##### Preparing Base Model

# %%
# Initialize the base model
base_model = transformers.Qwen2VLForConditionalGeneration.from_pretrained(
    base_model_name, torch_dtype=torch.float16, device_map="auto"
)

# Ensure the model is in evaluation mode
base_model.eval()

# %% [markdown]
# ##### Utility Functions

# %%
# User Instruction need to be formatted in a way for the model to understand
def preprocess(instruction: str, image_path: str, processor: transformers.AutoProcessor) -> transformers.BatchEncoding:
    # Opening Image
    image = Image.open(image_path)

    # System Instructions
    system_instruction = f"You are an assistant that describes the content of the image." 
    

    # Formatting the Chat
    chat = [
        {
            "role": "system",
            "content": [{"type": "text", "text": system_instruction}],
        },
        {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": {instruction}},
            ],
        }
    ]

    # Applying the Chat template
    text_prompt = processor.apply_chat_template(
        chat, add_generation_prompt=True, 
    )

    # Final Processing to be fed into Model
    model_inputs = processor(
        text=[text_prompt], images=[image], padding=True, return_tensors="pt" 
    )
    return model_inputs


# Model Response Generation (max length needs to be adjusted so that the model's response isn't cut off)
def generate_response(
    model_inputs, base_model: transformers.Qwen2VLForConditionalGeneration, processor: transformers.AutoProcessor, device:torch.device, max_new_tokens=512
):
    model_inputs = model_inputs.to(device)

    with torch.no_grad():
        generated_ids = base_model.generate(**model_inputs, max_new_tokens=max_new_tokens)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        output_texts = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

    return output_texts




# %% [markdown]
# ##### Model Output -> Image Description 
# 

# %%
# Preprocessing the image and instruction
processed_prompt = preprocess(
    instruction="What is the content of the image?",
    image_path=complete_test_image_data_path,
    processor=processor,
)

# Generating the response
decoded_output = generate_response(
    processed_prompt, base_model, processor, device, max_new_tokens=128
)

# %% [markdown]
# ##### Output Display (Change Later for Production)

# %%
print(decoded_output[0])


