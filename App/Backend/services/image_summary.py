""" services/image_summary """

# Imports
from PIL import Image
import torch
import numpy as np
import transformers

MIN_SIZE = 28  # From the error

def preprocess(instruction: str, image_np: np.ndarray,
               processor: transformers.AutoProcessor) -> transformers.BatchEncoding:
    """Preprocesses the image and prompt into the correct format for the VLM."""

    # Opening Image
    image = Image.fromarray(image_np)

    # --- Resize if too small ---
    if image.height < MIN_SIZE or image.width < MIN_SIZE:
        new_width = max(image.width, MIN_SIZE)
        new_height = max(image.height, MIN_SIZE)
        image = image.resize((new_width, new_height))

    # System Instructions
    system_instruction = "You are an assistant that returns a list of objects as strings in the image. Like so: ['car', 'tree', 'person']"

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
                {"type": "text", "text": instruction},
            ],
        }
    ]

    # Applying the Chat template
    text_prompt = processor.apply_chat_template(chat, add_generation_prompt=True)

    # Final Processing to be fed into Model
    model_inputs = processor(
        text=[text_prompt], images=[image], padding=True, return_tensors="pt" 
    )

    return model_inputs

def generate_response(model_inputs, base_model: transformers.Qwen2VLForConditionalGeneration,
                      processor: transformers.AutoProcessor, device:torch.device,
                      max_new_tokens=1024):
    """ Generates the desired text from the given image and prompt."""
    # Preparing device and setting inputs
    base_model.eval()
    model_inputs = model_inputs.to(device)

    # Performing generation and clipping
    with torch.no_grad():
        generated_ids = base_model.generate(**model_inputs, max_new_tokens=max_new_tokens)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        output_texts = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

    return output_texts[0]

def is_partial_match(user_item, predicted_set):
    return any(user_item in pred_item or pred_item in user_item for pred_item in predicted_set)
