import re

# Define the input and output file paths
code_path = "../code1"

input_file = f"{code_path}/model.h"
output_file = f"{code_path}/model.h"

# Read the content of the input file
with open(input_file, "r") as file:
    content = file.read()

# Modify the array definition
content = re.sub(r"unsigned char model_tflite\[\] = {", "#include <pgmspace.h>\nconst unsigned char model[] PROGMEM = {", content)

# Modify the length variable definition
content = re.sub(r"unsigned int model_tflite_len = (\d+);", r"const unsigned int model_len = \1;", content)

# Write the modified content to the output file
with open(output_file, "w") as file:
    file.write(content)

print(f"Modified file saved as {output_file}")
