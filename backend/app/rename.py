import os
from utils.slugify import slugify_filename

folder = r"F:\LV\ui\backend\data\posters"

for filename in os.listdir(folder):
    new_name = slugify_filename(filename)
    os.rename(f"{folder}/{filename}", f"{folder}/{new_name}")
    print(f"{filename} → {new_name}")
