#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "3"


# In[2]:


import torch 
from transformers import MT5Tokenizer, MT5ForConditionalGeneration

model_path_or_dir = "google/flan-t5-base"
tokenizer = MT5Tokenizer.from_pretrained(model_path_or_dir)
model = MT5ForConditionalGeneration.from_pretrained(model_path_or_dir, device_map="auto")


# In[3]:


'''
SelfAttention.q.weight
encoder.block.0.layer.0.SelfAttention.k.weight
encoder.block.0.layer.0.SelfAttention.v.weight
encoder.block.0.layer.0.SelfAttention.o.weight
'''
import os
from peft import get_peft_model, LoraConfig, PeftModel
model = PeftModel.from_pretrained(model, 'output')


# In[4]:


import torch
from IPython.display import display, Markdown
device = torch.device(0)

def display_answer(text):
    inputs = tokenizer(text, return_tensors="pt")
    inputs = inputs.to(device)
    pred = model.generate(**inputs, max_new_tokens=512)
    res = tokenizer.decode(pred[0], skip_special_tokens=True)
    display(Markdown(res))


# In[5]:


text = '### Human: Extract: \n\n\nRecord date: 2102-08-28\n\n\nGibson Internal Medicine Intern Admission Note\n\nPATIENT:  Grace Marvin Yandell\nMRN:  8099832\nADMIT DATE:  8/27/02\nPCP:  unknown\n\nCC:  tx from Mount San Rafael Hospital\n\nHPI:  80F with multiple medical problems including breast ca s/ ### Assistant:'
display_answer(text)


# In[ ]:


import json

with open("testing.json", 'r', encoding='utf8') as f:
    data_list = json.load(f)


for data in data_list:
    input_text = data["input"]
    inputs = tokenizer(input_text, return_tensors="pt")
    inputs = inputs.to(device)
    pred = model.generate(**inputs, max_new_tokens=512)
    output = tokenizer.decode(pred[0], skip_special_tokens=True)
    data["output"] = output
    print(data)


with open("testing_result.json", 'w', encoding='utf8') as f:
    json.dump(data_list, f, ensure_ascii=False)
    
    

