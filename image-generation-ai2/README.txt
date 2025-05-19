Documentation for generating images

Before starting make sure that you have all the files and folders in the same directory and named the same way otherwise os might not find the corresponding folders.
Best case if you use an IDE like visual studio code or else; that you make a folder there and put everything inside there.

1. Python Version
- Make sure to use the right python version which is capable of using libraries like cv2, sklearn and others seen in the generate_poc.py (For myself Im running it on Python 3.8.10)

2. Stable Diffusion
- Download the Automatic1111 stable diffusion webui from the link posted in the whatsApp group chat or use the following link (https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases/tag/v1.0.0-pre)
 - Download the sd.webui.zip
  - Extract folder to any place on the pc where its easy to find and use

3. Model
- Get a inpainting model which is capable of generating realistic images (Im using the Realistic_Vision_V5.1-inpainting.safetensor found on huggingface https://huggingface.co/SG161222/Realistic_Vision_V5.1_noVAE/blob/main/Realistic_Vision_V5.1-inpainting.safetensors)
 - The model should be a safetensor
  - Safe the safetensor file in the extracted stable diffusion folder under "...\sd.webui\webui\models\Stable-diffusion"

4. Start and selecting model
- Once done you go into the sd.webui folder and run the update.bat and afterwards the run.bat
 - Once you are on the local webserver you can choose your model in the top-left corner and select it and click on the icon right next to it to make it a checkpoint
  - Now close the local webserver aswell as the cmd 

5. COMMANDLINE-ARGS
- Go into sd.webui and afterwards into the webui folder and head to the webui-user.bat und open it with a Texteditor (Default Windows Editor works fine)
 - Necessary arguments you wanna give over are "--precision full --no-half --api" (--api for the api usage and --precision full --no-half for prefenting artefacts in the vram usage)
  - There is also --xformers for RTX graphiccards to make the process faster but didnt work for me and made the results slightly worse in my opinion
   - There is also --medvram or --lowvram if vram capacity is to low

6. Webui
- If all the steps are done correctly you can start the webui-user.bat which should be basically the same as run.bat but Im only running the webui-user.bat
 - You can see if you are using the right model if the cmd is giving a line saying something like that: "Loading weights [befb05f117] from C:\Users\spook\OneDrive\OneDrive\Desktop\sd.webui\webui\models\Stable-diffusion\Realistic_Vision_V5.1-inpainting.safetensors"
  - You can always close the local webserver 

7. Pipeline
- fill the clean_images folder with clean images of any size
 - adjust the gen_config.json for parameters you want to change
- start the auto_mask.py to generate random masks (maybe this script needs to be called within the generate_poc.py before looping over the images?)
- start the generate_poc.py to generate weird images
  - the settings Im using are Pretty consistent but if anybody finds other ones which are better let the group know 
   - dont be scared to stop the generation proccess because I implemented a checking loop which checks the names of the weird images and wont start generating a new weird Image on the same clean Image(as Long the weird Image is in the 	dataset folder)

Version 2:

1. Overview
 - Integrated Controlnet for improvement of object placement with edge maps
 - Updated generate_poc.py; gen_config.json and added canny.py for the function which does the edge Maps

2. Installation
 - Open WebUI and browse the extension tab for sd-webui-controlnet and install it (Extension -> Available -> Load From … -> sd-webui-controlnet)
 - Refresh the Extensions under Extension -> Installed and afterward close the WebUI aswell as the cmd
 - Download the ControlNet Module (https://huggingface.co/webui/ControlNet-modules-safetensors/blob/main/control_canny-fp16.safetensors)
 - Place it into stable-diffusion-webui/models/ControlNet/
