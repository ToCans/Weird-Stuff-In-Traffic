""" App/Backend/schemas/images.py"""
from pydantic import BaseModel

########################
###### Generation ######
########################

class ImageGenerationPrompt(BaseModel):
    """Request body for image generation request."""
    prompt: str

class GeneratedImage(BaseModel):
    """Single image prompted for image generation."""
    prompt: str
    imageBase64: str

class GeneratedImages(BaseModel):
    """Response body for image generation."""
    images: list[GeneratedImage]

########################
###### Detection  ######
########################

class DetectionRequest(BaseModel):
    """Request body for image detection."""
    prompt: str
    imageBase64: str

class DetectionResponse(BaseModel):
    """Response body for image detection."""
    prompt: str
    imageBase64: str
    score: float
