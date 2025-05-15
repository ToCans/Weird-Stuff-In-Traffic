from diffusers import StableDiffusionXLInpaintPipeline, DPMSolverMultistepScheduler
import torch
from PIL import Image, ImageDraw, ImageFilter

def create_mask_image(img_w, img_h, x1, y1, x2, y2):
    mask = Image.new("L", (img_w, img_h), 0)
    
    draw = ImageDraw.Draw(mask)
    draw.rectangle([x1, y1, x2, y2], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(50))
    return mask

pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
    "change/to/model/location",   # change path
    torch_dtype=torch.float16,
    variant="fp16",
    safety_checker=None
).to("cuda")

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

negative_prompt = "blurry, artifacts, distorted, mutated, extra limbs, extra objects, low quality, bad composition, background change, duplicated, cloned"
styling_prompt = ", realistically integrated into a real-world Street scene, preserving the original background, lighting, camera angle and perspective"
negative_prompt = "blurry, artifacts, distorted, extra limbs, low quality, unrealistic, ugly"
styling_prompt = ", street view, scene, photography, detailed, high quality, near the camera"


def realvisxl_inpaint(x1, y1, x2, y2, image, user_prompt):

    mask_image = create_mask_image(image.size[0], image.size[1], x1, y1, x2, y2)

    # visualize mask for inpainting
    # draw = ImageDraw.Draw(mask_image)
    # draw.rectangle((x1, y1, x2, y2), outline='green', width=5)
    # mask_image.save("G:/weirdstuffintraffic/mask_image.png")

    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    result = pipe(
    prompt=user_prompt + styling_prompt,
    negative_prompt=negative_prompt,
    image=image,
    mask_image=mask_image,
    strength=0.6,
    num_inference_steps=40,
    guidance_scale=7.0,
    height=896,
    width=1600,
    inpaint_full_res=True,
    inpaint_full_res_padding=32,
    generator=torch.Generator("cuda").manual_seed(42)
    )

    return result.images[0]