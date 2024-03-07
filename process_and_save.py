import json

import os
import re
from collections import defaultdict
import re
import json
from collections import defaultdict
import re
import string
from logging.handlers import TimedRotatingFileHandler

import xml.etree.ElementTree as ET
import re

import os
def word_to_word(big_directory, save_directory):
    for root, dirs, files in os.walk(big_directory):

        for file in files:
            if file.endswith(".json"):
                file_name_with_extension = file
                file_name_without_extension = os.path.splitext(file)[0]
                print(file_name_without_extension)
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_contents = defaultdict(str)
                    file_outputs = defaultdict(str)
                    for entry in data:
                        content = entry["input"]

                        # 移除指定的标签
                        content = re.sub(r'### Human: Extract: ', '', content)
                        content = re.sub(r' ### Assistant:', '', content)

                        # 提取并处理输出值
                        output_values = entry["output"].split('|')
                        output_values = sorted(output_values, key=len, reverse=True)
                        output_values = list(set(output_values))
                        c = ""

                        for pair in output_values:
                            if ':' in pair:  # 确保这是一个有效的键值对
                                _, output_value = pair.split(':', 1)
                                output_value = output_value.strip()  # 移除前后的空白字符
                                output_value = re.escape(output_value)
                                output_value = output_value.strip(string.punctuation)

                                pattern = r'\b\w*?' + output_value.replace(r'\ ', r'\s*').replace(r'\:', r'\s*:\s*') + r'\w*\b'

                                content = re.sub(pattern, '[REDACTED]', content, flags=re.IGNORECASE)

                        file_contents[entry["filename"]] += content+''
                        file_outputs[entry["filename"]] += entry["output"] + '|'
                # 保存处理后的数据

                    save_path = save_directory + file_name_without_extension +"/"
                    print(save_path)
                    if not os.path.exists(save_directory + file_name_without_extension):
                        os.makedirs(save_directory + file_name_without_extension)
                    for filename, content in file_contents.items():
                        filename, _ = filename.split('.', 1)
                        full_path = save_path + filename + ".txt"
                        with open(full_path, 'w', encoding="utf-8") as f:
                            f.write(content)

big_directory = "data/result"
save_directory = "data/result_text_word/"
word_to_word(big_directory, save_directory)