from logging.handlers import TimedRotatingFileHandler

import xml.etree.ElementTree as ET
import re

import os
files_needed = [
    "380-03.txt", "162-02.txt", "193-04.txt", "371-05.txt", "349-01.txt", 
    "347-04.txt", "234-01.txt", "345-01.txt", "236-04.txt", "238-01.txt", 
    "263-05.txt", "113-02.txt", "191-01.txt", "373-01.txt", "113-03.txt", 
    "263-04.txt", "236-05.txt", "210-01.txt", "310-01.txt", "312-04.txt", 
    "193-05.txt", "162-03.txt", "137-02.txt", "202-01.txt", "380-02.txt", 
    "202-03.txt", "139-05.txt", "162-01.txt", "111-04.txt", "349-02.txt", 
    "234-02.txt", "210-03.txt", "310-03.txt", "345-02.txt", "238-02.txt", 
    "160-04.txt", "191-02.txt", "113-01.txt", "373-03.txt", "373-02.txt", 
    "191-03.txt", "160-05.txt", "135-04.txt", "382-04.txt", "238-03.txt", 
    "345-03.txt", "310-02.txt", "210-02.txt", "234-03.txt", "349-03.txt", 
    "139-04.txt", "202-02.txt", "380-01.txt", "137-01.txt", "162-04.txt", 
    "371-03.txt", "193-02.txt", "111-01.txt", "347-02.txt", "212-03.txt", 
    "312-03.txt", "263-03.txt", "236-02.txt", "200-03.txt", "113-05.txt", 
    "200-02.txt", "382-01.txt", "135-01.txt", "236-03.txt", "263-02.txt", 
    "312-02.txt", "212-02.txt", "347-03.txt", "193-03.txt", "371-02.txt", 
    "137-04.txt", "162-05.txt", "139-01.txt", "139-03.txt", "111-02.txt", 
    "193-01.txt", "347-01.txt", "349-04.txt", "234-04.txt", "345-04.txt", 
    "238-04.txt", "236-01.txt", "135-03.txt", "373-05.txt", "191-04.txt", 
    "373-04.txt", "200-01.txt", "382-02.txt", "160-03.txt", "316-02.txt", 
    "216-02.txt", "343-03.txt", "384-04.txt", "208-02.txt", "197-03.txt", 
    "375-02.txt", "204-02.txt", "386-01.txt", "131-01.txt", "388-04.txt", 
    "232-03.txt", "267-02.txt", "267-03.txt", "232-02.txt", "119-01.txt", 
    "379-03.txt", "388-05.txt", "204-03.txt", "375-03.txt", "197-02.txt", 
    "115-01.txt", "166-04.txt", "208-03.txt", "168-01.txt", "343-02.txt", 
    "216-03.txt", "216-01.txt", "316-01.txt", "318-04.txt", "218-04.txt", 
    "265-04.txt", "206-04.txt", "168-03.txt", "208-01.txt", "115-03.txt", 
    "199-05.txt", "375-01.txt", "204-01.txt", "386-02.txt", "164-03.txt", 
    "379-01.txt", "119-03.txt", "314-04.txt", "341-05.txt", "269-04.txt", 
    "267-01.txt", "232-01.txt", "341-04.txt", "314-05.txt", "164-02.txt", 
    "131-03.txt", "386-03.txt", "199-04.txt", "197-01.txt", "168-02.txt", 
    "218-05.txt", "343-01.txt", "318-01.txt", "218-01.txt", "316-04.txt", 
    "265-01.txt", "166-03.txt", "206-01.txt", "384-02.txt", "197-05.txt", 
    "388-02.txt", "204-04.txt", "377-01.txt", "214-01.txt", "314-01.txt", 
    "267-04.txt"
]

def error_analysis_and_save(ground_truth, save_directory, result_file):

    # global vars for counting
    error_numbers = {}
    type_numbers = {}
    tot_false_neg = 0
    tot_false_pos = 0
    tot_true_neg = 0
    tot_true_pos = 0


    def read_text_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content


    def compare(gpt_path, answer_path):
        # ALSO need to split PHI!!!!! (this way each word is one phi even or a two word name)

        # xml tree stuff
        ans_root = ET.parse(answer_path).getroot()
        tags = ans_root.find('TAGS').findall('*')
        gt_text = ans_root.find('TEXT').text
        text = read_text_file(gpt_path)
        # print(gt_text)

        errors = {}
        under_redact = 0
        over_redact = 0
        # len(tags)  # expected; correct --> but need to account for multi word tags
        total_redact = 0
        # total_words = len(text.split())
        # gt_text = gt_text.split()
        # #WITHOUT RANDOM:
        final_gt_text = re.findall(r'\b\w+\b', gt_text)
        total_words = len(final_gt_text)#len(text.split())
        #---------

        #WITH random removal:
        total_words = len(text.split())
        # print("total words: \n")
        # print(total_words)
        # true_neg = 0

        # calculate expected redact
        for tag in tags:
            tag_text = tag.get('text')
            total_redact += len(tag_text.split())  # expected

        # print("total redact")
        # print(total_redact)

        # count total words that are not redacted (to calculate true negatives)
        # DOUBLE CHECK THIS
        # for line in text.splitlines():
        #     for word in line.split():
        #         if word != "[REDACTED]":
        #             total_words += 1

        # count over redacts and keep them in a counter
        for line in text.splitlines():
            # right now, over_redact == total number of '[REDACTED]'
            over_redact += line.count("[REDACTED]")

        # for tag in tags:
        #     tag_text = tag.get('text')
        #     tag_text = tag_text.split()
        #     for tag in tag_text:
        #         tags_global.append(tag)
        # under redact simple counter

        # NEW: (Changed the under_redact count to count each phi individually by length of phi)
        for tag in tags:
            tag_type = tag.get('TYPE')
            tag_text = tag.get('text')
            if text.find(tag_text) != -1:
                # this adjustment should count each word instead of each phi
                under_redact += len(tag_text.split())

        # Old:
        # for tag in tags:
        #     tag_type = tag.get('TYPE')
        #     tag_text = tag.get('text')
        #     if text.find(tag_text) != -1:
        #         under_redact += 1
                # Uncomment to dump false negatives types
                # with open("updating_false_neg.txt", "a") as f:
                #     f.write(str(tag_type) + ": " + str(tag_text) + " \n")
                    #can just comment this out when done dumping files

        # count under redacts and keep them in a dictionary
        for tag in tags:
            tag_type = tag.get('TYPE')
            tag_text = tag.get('text')
            # count total number redacts by type
            if tag_type in type_numbers:
                type_numbers[tag_type] += 1
            else:
                type_numbers[tag_type] = 1

            if text.find(tag_text) == -1:  # phi successfully redacted
                continue
            else:  # phi not redacted
                # add errors to list
                if tag_type in errors:
                    errors[tag_type] += [tag_text]
                else:
                    errors[tag_type] = [tag_text]

                # add to global counter for errors
                if tag_type in error_numbers:
                    error_numbers[tag_type] += 1
                else:
                    error_numbers[tag_type] = 1
                # under_redact += 1 --> now done above

        # over redact: = count of [redacted] in text - correct redacts (which is expected number of redacts - missed redacts)
        over_redact = over_redact - (total_redact - under_redact)
        # avoids negative calculations that occasionally result
        over_redact = max(over_redact, 0)
        # confusion matrix calculations
        false_neg = under_redact
        false_pos = over_redact
        true_pos = total_redact - under_redact
        # NEW --> changed this to take the total words and subract the true positives (i think its right but if not its really close)
        # should be total words - (false neg (any left over PHI) + true pos + false pos (any instance of redacted))
        true_neg = total_words - (false_neg + true_pos + false_pos)
        #for 100: total words should equal false neg + true pos

        #temp fix:
        if true_neg < 0:
            true_neg = 0

        #could also print total words

        # Figure out if file should be looking at xml or text or both for metrics

        precision, recall, f1, neg_predecitive_val = metrics_calc_new(
            false_neg, false_pos, true_neg, true_pos)

#        print("File: " + gpt_path.split('/')[-1])
#        print("False negatives: ", false_neg)
#         print("True negatives: ", true_neg)
#         print("False positives: ", false_pos)
#         print("True positives: ", true_pos)
#         print("Precision: ", precision)
#         print("Recall: ", recall)
#         print("F1: ", f1)
#         print("NPV: ", neg_predecitive_val)
        
#        print("List of Errors: " + str(errors))
#        print("---")
#         for category, values in errors.items():
#             if len(values) > 1:
#                 for value in values:
#                     print(f"{category}: {value}")
#             else:
#                 print(f"{category}: {', '.join(values)}")

        return false_neg, false_pos, true_neg, true_pos, total_redact


    def metrics_calc_new(false_neg, false_pos, true_neg, true_pos):
        precision = true_pos / (true_pos + false_pos)
        recall = true_pos / (true_pos + false_neg)
        f1 = 2 * (precision * recall) / (precision + recall)
        if true_neg + false_neg == 0:
            neg_predecitive_val = 0
        else:
            neg_predecitive_val = true_neg / (true_neg + false_neg)

        return precision, recall, f1, neg_predecitive_val


    def calc_type_accuracy():
        type_accuracy = {}
        false_neg_per_cat = {}
        true_neg_per_type = {}
        npv_per_type = {}
        true_pos_per_type = {}
        recall_by_type = {}

        # error_numbers[type]: count of errors of specific type
        # type_numbers[type] total count of that type in the ground truth.

        for type in type_numbers.keys():
            # *general accuracy: 1 - errors/total_tags_per_type

            type_accuracy[type] = 1 - \
                (error_numbers.get(type, 0) / type_numbers[type])

            false_neg_per_type = type_numbers[type] - error_numbers.get(type, 0)
            false_neg_per_cat[type] = type_numbers[type] - false_neg_per_type

            # true_neg_per_type[type] = false_neg_per_type

            # true_pos_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

            # Calculate true negatives for each type
            true_pos_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

            # Calculate true positives for each type
            # true_neg_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

            # npv_per_type[type] = true_neg_per_type[type] / \
            #     (true_neg_per_type[type] + false_neg_per_cat[type])

            recall_by_type[type] = true_pos_per_type[type] / \
                (true_pos_per_type[type]+false_neg_per_cat[type])

            # true_pos: total number of tags for a type - number under redacts for a type

        return type_accuracy, false_neg_per_cat, true_neg_per_type, true_pos_per_type, npv_per_type, recall_by_type


    if __name__ == "__main__":
        result_file = result_file + \
                      save_directory.split('/')[-2]+'.txt'
        #print(result_file)
        print(save_directory.split('/')[-2])

        #gpt_redact = [os.path.join(save_directory, f) for f in os.listdir(save_directory) if os.path.isfile(os.path.join(save_directory, f))]
        #print(gpt_redact)
        # Using list comprehension to generate the full paths of only the files you need
        gpt_redact = [os.path.join(save_directory, f) for f in files_needed if os.path.isfile(os.path.join(save_directory, f))]
        # print(gpt_redact)
        answers = []
        for file in gpt_redact:

            # this is the gound truth values (with / at the end)
            ans = ground_truth + \
                file.split('/')[-1].split('.')[0] + '.xml'
            answers.append(ans)

#         print("----------------------------\n\n")
#         print("ERROR ANALYSIS\n\n")
#         print("----------------------------\n\n")

        # loop through directories and compare files
        for (gpt, ans) in zip(gpt_redact, answers):
            # make sure folders are aligned by name
            if gpt.split('/')[-1].split('.')[0] != ans.split('/')[-1].split('.')[0]:
                print("FILES NOT ALIGNED: CHECK GPT AND ANSWERS FOLDER ORDER")
                break

            # mistakes, under_redacts, over_redacts = compare(gpt, ans)

            false_neg, false_pos, true_neg, true_pos, total_redact = compare(
                gpt, ans)
            tot_false_neg += false_neg
            tot_false_pos += false_pos
            tot_true_neg += true_neg
            tot_true_pos += true_pos

        # calculate accuracy breakdown by type:
        type_accuracy, false_neg_per_cat, true_neg_per_type, true_pos_per_type, npv_per_type, recall_per_type = calc_type_accuracy()
        precision, recall, f1, neg_predecitive_val = metrics_calc_new(
            tot_false_neg, tot_false_pos, tot_true_neg, tot_true_pos)

        print("------------------------------------------------------------\n\n")
        print("OVERALL RESULTS\n\n")
        print("Number of Files Analyzed: " + str(len(gpt_redact)))
        print("\n")
        print("Total Number of False Positives: " + str(tot_false_pos))
        print("Total Number of False Negatives: " + str(tot_false_neg))
        print("Total Number of True Positives: " + str(tot_true_pos))
        print("Total Number of True Negatives: " + str(tot_true_neg))
        print("\n")
        print("Precision: ", precision)
        print("Recall: ", recall)
        print("F1: ", f1)
        print("NPV: ", neg_predecitive_val)
        print("\n")
        print("Recall Breakdown by Error Type: " + str(recall_per_type) + "\n")
        # print("True Negatives by Error Type: " + str(true_neg_per_type) + "\n")
        print("True Positives by Error Type: " + str(true_pos_per_type) + "\n")
        print("False Negatives by Error Type: " + str(false_neg_per_cat) + "\n")
        # print("NPV by Error Type: " + str(npv_per_type) + "\n\n")

        # precision breakdown by error type
        # f1 breakdown by error type
        # npv breakdown by error type
        # ^^ if possible

result_file = 'data/result_text/'
save_directory = 'data/result/'
ground_truth = 'data/ground_truth/'
for root, dirs, files in os.walk(save_directory):

    root = root +"/"
    if root !=  "/Users/janceyliu/Desktop/lifespan/t5-ner3/forgpt/result_text11.30//" :
        print(root)
        error_analysis_and_save(ground_truth, root, result_file)