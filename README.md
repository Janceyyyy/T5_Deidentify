# T5 Patient Information De-identification System

## Overview

This project leverages the powerful T5 (Text-to-Text Transfer Transformer) model for the de-identification of patient information in medical records. Compared to other models, the T5's performance in recognizing and anonymizing personal identifiers within text data is unparalleled, ensuring higher privacy and security levels in processing sensitive medical records.

## Installation and Environment Setup

1. **Clone the project repository:**
    ```bash
    git clone [repository URL]
    ```

2. **Navigate to the project directory:**
    ```bash
    cd [project name]
    ```

3. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Data Preparation

Before fine-tuning the model or making predictions, prepare your data using the `data_preprocessing.py` script. This script processes the input data into a consolidated JSON file and breaks down sentences to facilitate further processing.

To execute data preprocessing:
```bash
python data_preprocessing.py --input_dir [your input directory] --output_file [desired output file]
  ```
  
  ## Fine-Tuning the Model

To adapt the T5 model specifically to the task of de-identifying patient information within your dataset, you'll need to fine-tune the model. This section assumes you have a script named `finetune.py` (or similar) ready for this purpose. Adjust the command and script name as necessary based on your project's actual setup.

```bash
python finetune.py --data_file [path to your JSON data file] --model_name_or_path [pretrained model path or identifier]
  ```
  
  Make sure to replace `[path to your JSON data file]` with the path to the JSON file prepared during the data preparation step, and [pretrained model path or identifier] with the path or identifier of the T5 model you are using.
  
 ## Making Predictions
Once the model has been fine-tuned, you can use it to make predictions on new, unseen data. This typically involves a script, possibly named infer.py, which loads the fine-tuned model and processes input data to generate de-identified outputs.

```bash

python infer.py --model_dir [your model directory] --input_data [path to your data file]

  ```
Replace `[your model directory]` with the directory containing your fine-tuned model and `[path to your data file]` with the path to the data on which you wish to make predictions.


## Results Analysis
After making predictions, you'll want to assess the performance of the model and the effectiveness of the de-identification process. This can be done using the following scripts:

### Processing and Saving Results:

Use `process_and_save.py` to process the prediction results and save them in a structured format.

```bash
python `process_and_save.py` --input_file [your prediction file] --output_dir [directory to save processed files]
  ```
  
### Error Analysis:

The `error_analysis.py` script can be used to perform a detailed analysis of the errors made by the model, helping to understand its performance characteristics and areas for improvement.

```bash
python error_analysis.py --input_file [your processed results file] --report_file [error analysis report]
  ```
  
  