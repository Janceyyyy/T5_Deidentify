#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.environ["CUDA_VISIBLE_DEVICES"] = "3"


# In[2]:


import torch 
from transformers import MT5Tokenizer, MT5ForConditionalGeneration

model_path_or_dir = "google/flan-t5-base"
tokenizer = MT5Tokenizer.from_pretrained(model_path_or_dir)
model = MT5ForConditionalGeneration.from_pretrained(model_path_or_dir, device_map="auto")





# In[4]:


'''
SelfAttention.q.weight
encoder.block.0.layer.0.SelfAttention.k.weight
encoder.block.0.layer.0.SelfAttention.v.weight
encoder.block.0.layer.0.SelfAttention.o.weight
'''
import os
from peft import get_peft_model, LoraConfig, PeftModel

if os.path.exists('output111'):
    model = PeftModel.from_pretrained(model, 'output111')
else:
    target_modules = ["SelfAttention.q", "SelfAttention.k", "SelfAttention.v"]
    peft_config = LoraConfig(
        task_type="SEQ_2_SEQ_LM",
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=target_modules,
    )
    model = get_peft_model(model, peft_config)


# In[5]:


model.supports_gradient_checkpointing = True
model.gradient_checkpointing_enable()
model.enable_input_require_grads()
model.config.use_cache = False
model.isparallelizable = True
model.model_parallel = True
model.print_trainable_parameters()


# In[6]:


import json, datasets
from tqdm import tqdm
    
def preprocess(tokenizer, file_path, max_seq_length, skip_overlength=False):
    with open(file_path, 'r', encoding='utf8') as f:
        data_list = json.load(f)
    for data in tqdm(data_list):
        input_ids = tokenizer.encode(data["input"], max_length=max_seq_length, truncation=True, add_special_tokens=False)
        labels = tokenizer.encode(data['output'], max_length=max_seq_length, truncation=True)
        yield {
            "input_ids": input_ids,
            "labels": labels,
        }
        
trainset = datasets.Dataset.from_generator(lambda: preprocess(tokenizer, "whole_training_dataset.json", 1024))
print(trainset)


# In[7]:


def data_collator(features):
    len_ids = [len(feature["input_ids"]) for feature in features]
    len_labels = [len(feature["labels"]) for feature in features]
    longest_id = max(len_ids)
    longest_label = max(len_labels)
    input_ids = []
    labels_list = []
    
    for ids_l, lables_l, feature in sorted(zip(len_ids, len_labels, features), key=lambda x: -x[0]):
        ids = feature["input_ids"]
        labels = feature["labels"]
        ids = ids + [tokenizer.pad_token_id] * (longest_id - ids_l)
        labels = labels + [-100] * (longest_label - lables_l)
        input_ids.append(torch.LongTensor(ids))
        labels_list.append(torch.LongTensor(labels))

    return {
        "input_ids": torch.stack(input_ids),
        "labels": torch.stack(labels_list),
    }


# In[8]:


from transformers import TrainingArguments, Trainer

class ModifiedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        return model(
            input_ids=inputs["input_ids"],
            labels=inputs["labels"],
        ).loss
    
    def save_model(self, output_dir=None, _internal_call=False):
        self.model.save_pretrained(output_dir)


# In[24]:


batch_size = 25
train_args = TrainingArguments(learning_rate=1e-3, 
                               per_device_train_batch_size=batch_size, 
                               gradient_accumulation_steps=2,
                               max_steps=780,
                               save_steps=600,
                               logging_steps=10,
                               output_dir="wandb",
                               remove_unused_columns=False,
                              )

trainer = ModifiedTrainer(
    model=model,
    train_dataset=trainset,
    args=train_args,
    data_collator=data_collator,
)
trainer.train()
model.save_pretrained("./output")

