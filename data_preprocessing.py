import os
import json
from tqdm import tqdm
import xml.etree.ElementTree as ET
import nltk
nltk.download("stopwords")
import os
import xml.etree.ElementTree as ET
import nltk
from nltk.corpus import stopwords
import random
import re

def extract_data_from_xml(xml_text):
    root = ET.fromstring(xml_text)

    text_content = root.find(".//TEXT").text

    tags_elements = root.findall(".//TAGS/*")
    tags = [{
        'id': tag.get('id'),
        'start': int(tag.get('start')),
        'end': int(tag.get('end')),
        'text': tag.get('text'),
        'type': tag.tag.upper(),
        'comment': tag.get('comment')
    } for tag in tags_elements]

    return text_content, tags



def segment_text_with_tags(text, tags):
    l = len(text) // len(text)
    if l == 0:
        third_length = len(text)
    else:
        third_length = len(text) // l

    segments = []

    i = 0
    while i < len(text):
        end_idx = i + third_length
        if end_idx > len(text):
            end_idx = len(text)
        while any(tag['start'] <= end_idx < tag['end'] for tag in tags):
            end_idx += 1

        segment_text = text[i:end_idx]
        matching_tags = [
            tag for tag in tags if tag['start'] >= i and tag['end'] <= end_idx
        ]

        segments.append({
            'text': segment_text,
            'tags': matching_tags
        })

        i = end_idx

    return segments


def whole_tags(text, tags):
    return [{
        'text': text,
        'tags': tags
    }]

def remove_stop_words(file):

    stop_words = set(stopwords.words('english'))

    text = file
    lines = text.splitlines()
    new_text = []
    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower()
                       not in stop_words]
        new_text.append(' '.join(clean_words))
    return '\n'.join(new_text)




def extract_and_replace_phi(note, phi_tags):
    phi_data = []
    modified_note = note
    offset = 0


    for tag in phi_tags:

        start = int(tag["start"])
        end = int(tag["end"])
        phi_text = note[start:end]
        phi_data.append((start, phi_text,tag["type"]))

        # Replace PHI text with placeholder and adjust the offset
        modified_note = modified_note[:start + offset] + "<PHI>" + modified_note[end + offset:]

        offset += len("<PHI>") - len(phi_text)

    return modified_note, phi_data
def random_remove_words(note, tag,percentage):

    words = note.split()
    non_phi_words = [i for i, word in enumerate(words) if "<PHI>" not in word]
    total_remove = int(len(non_phi_words) * percentage)

    remove_indices = random.sample(non_phi_words, total_remove)

    # Rebuilding the note excluding the words at the removed indices
    text = ' '.join([word for i, word in enumerate(words) if i not in remove_indices])
    return text
def remove_stop_words(note):

    stop_words = set(stopwords.words('english'))

    text = note
    lines = text.splitlines()
    new_text = []
    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower()
                       not in stop_words]
        new_text.append(' '.join(clean_words))
    return '\n'.join(new_text)
def split_and_reinsert_phi(note, phi_data, segment_length):
    segments = []
    start_index = 0

    while start_index < len(note):
        end_index = min(start_index + segment_length, len(note))
        if end_index < len(note) and "<PHI>" in note[end_index-5:end_index+5]:
            print(end_index,note[end_index],note[end_index-5:end_index+5])
            if note[end_index] == "<":
                end_index -= 1
            elif note[end_index] == "P":
                end_index -= 2
            elif note[end_index] == "H":
                end_index -= 3
            elif note[end_index] == "I":
                print("111")
                if end_index < len(note):
                    end_index += 2
                else:
                    end_index = len(note)
            elif note[end_index] == ">":
                if end_index < len(note):
                    end_index += 1
                else:
                    end_index = len(note)

            else:
                end_index = end_index
            print(note[end_index-5:end_index+5])


        # 添加分割的段落
        segments.append(note[start_index:end_index])
        start_index = end_index

    # 替换每个段落中的 <PHI> 占位符，并记录每个段落的 PHI 信息
    segment_phi_info = []
    re = []
    phi_index = 0
    phi_count = sorted(phi_data, key=lambda x: x[0])
    for segment_index, segment in enumerate(segments):
        phi_count = segment.count("<PHI>")
        segment_phis = []
        for _ in range(phi_count):
            # 替换占位符，并记录 PHI 信息
            phi_text = phi_data[phi_index][1]
            segment = segment.replace("<PHI>", phi_text, 1)
            segment_phis.append( phi_data[phi_index][2] + ': ' + phi_text)
            phi_index += 1
        segment_phi_info.append(segment_phis)

        re.append({
                'text': segment,
                'tags': sorted(segment_phis, key=lambda x: x.split(': ')[0])
            })

    return re

def reinsert_phi(note, phi_data):
    phi_data_sorted = sorted(phi_data, key=lambda x: x[0])
    for _, phi_text in phi_data_sorted:
        note = note.replace("<PHI>", phi_text, 1)
    return note

def read_and_process_files(directory):
    all_result = []
    test_input = []
    print(len(os.listdir(directory)))
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                print(filename)
                content = file.read()
                text_data, tags_data = extract_data_from_xml(content)
                #segments = segment_text_with_tags(text_data, tags_data)
                #print(tags_data)

                #segments = whole_tags(text_data, tags_data)
                note_with_placeholders, phi_data = extract_and_replace_phi(text_data, tags_data)
                #print(note_with_placeholders)
                #segments = random_remove_words(note_with_placeholders, phi_data, )
                segments = remove_stop_words(note_with_placeholders)


                #text = reinsert_phi(segments, phi_data)
                segments = split_and_reinsert_phi(segments, phi_data, 256)



                #print(phi_data,len(phi_data))
                for segment in segments:




                    all_result.append({
                        'filename': filename,
                        'input': '### Human: Extract: ' + segment["text"] + ' ### Assistant:',
                        'output': ' | '.join(segment["tags"] )

                    })

                    #tags = [item['text'] for item in tags_data]
            # tags = tags_data[“text”]
            # print(text)
                    # for phi in tags:
                    #     if phi not in text:
                    #         print(filename + "FAILED — PHI MISSING:" + phi)

                    #test_input.append()

    return all_result

paths = [' path']
all_results = []

for path in paths:
    results_from_path = read_and_process_files(path)
    all_results.extend(results_from_path)

json_object = json.dumps(all_results, indent=4)

# Writing to sample.json
with open("/data/testing.json", "w") as outfile:
    outfile.write(json_object)