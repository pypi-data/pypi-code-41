from flask import Flask, render_template, request, Markup, jsonify
from werkzeug.utils import secure_filename
import os
import pathlib
import re
import codecs
import json
import shutil
from collections import defaultdict
import glob
import nltk
import pandas as pd
from pandas import DataFrame
import numpy as np
import math
from importlib import reload
from zipfile import ZipFile

from sklearn.model_selection import train_test_split
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from textblob import Word

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


from sklearn.naive_bayes import MultinomialNB
import sys
reload(sys)
# sys.setdefaultencoding('utf8')

app = Flask(__name__)
UPLOAD_DIR = './data/uploads/'
INPUT_CSV_DIR = './data/csv/'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['ipynb', 'zip', 'txt'])


def create_fresh_path(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)
    return


create_fresh_path(UPLOAD_DIR)
create_fresh_path(INPUT_CSV_DIR)


def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_ipynb_file(dataset_path, student_id, exam_name):
    ipynb_file = ""
    path_to_ipynb = dataset_path + "/" + \
        str(student_id) + "/" + exam_name + "/"

    filenames = os.listdir(path_to_ipynb)
    for filename in filenames:
        if allowed_file(filename):
            ipynb_file = filename
    return path_to_ipynb, ipynb_file


def jupyter_to_csv(dataset_path, student_ids, exam_name_lst):
    global exam_name
    exam_name = ""
    for name in exam_name_lst:
        exam_name = exam_name+name

    student_ids.sort()
    id_for_ans = []
    ques_num = []
    ques = []
    answers = []
    checksums = []

    for student_id in student_ids:
        count = 0
        path_to_ipynb, ipynb_file = get_ipynb_file(
            dataset_path, student_id, exam_name)

        with open(path_to_ipynb + ipynb_file) as json_file:
            source_is_ans = False
            data = json.load(json_file)
            for (index, cell) in enumerate(data['cells']):
                if 'nbgrader' in cell['metadata'] and cell['metadata']['nbgrader']['solution'] == False \
                        and cell['metadata']['nbgrader']['grade'] == False:

                    next_cell = data['cells'][index+1]
                    if 'nbgrader' in next_cell['metadata'] and next_cell['metadata']['nbgrader']['solution'] == True:
                        count = count+1
                        current_question = "Question_"+str(count)
                        ques_num.append(current_question)
                        checksum_of_question = cell['metadata']['nbgrader']["checksum"]
                        checksums.append(checksum_of_question)
                        # ques.append(cell['source'][2])
                        ques_source = cell['source']
                        question = ''
                        for string in ques_source:
                            if "\n" in string or string.endswith('\n'):
                                string = string.replace('\n', '  ')
                            question = question+string
                        ques.append(question)

                        ans_source = next_cell['source']
                        ans = ''
                        for string in ans_source:
                            ans = ans+string
                        answers.append(ans)
                        id_for_ans.append(student_id)
                    else:
                        continue

    data = {'student_id': id_for_ans,
            'question_number': ques_num,
            'checksum_of_question': checksums,
            'question': ques,
            'answers':  answers}

    df = DataFrame(data, columns=[
                   'student_id', 'question_number', 'checksum_of_question', 'question', 'answers'])
    df.to_csv(INPUT_CSV_DIR+'all_data.csv', encoding='utf-8')

    df1 = df.sort_values(by='question_number')
    df1.set_index(keys=['question_number'], drop=False, inplace=True)
    q_nums = df1['question_number'].unique().tolist()

    unique_questions = df["checksum_of_question"].unique().tolist()
    for q_num in q_nums:
        q = df1.loc[df1.question_number == q_num]
        q.to_csv(INPUT_CSV_DIR+q_num+'.csv', encoding='utf-8')

    return q_nums, unique_questions


def get_model_answers(filename):
    global model_answers
    count = 0
    answer_file = open(filename)
    read_file = answer_file.readlines()
    for line in read_file:
        temp = line.strip()
        ans = temp[5:]
        count = count+1
        question_number = "Question_"+str(count)
        model_answers[question_number] = ans
    return model_answers


def read_csv(filename):
    data = pd.read_csv(filename)
    list_corpus = data["answers"].tolist()
    list_labels = [''] * len(list_corpus)

    return data, list_corpus, list_labels


def safe_strings():
    global list_corpus
    for idx in range(len(list_corpus)):
        ans = list_corpus[idx]
        if pd.isnull(ans) or ans == "YOUR ANSWER HERE":
            ans = "NO ANSWER PROVIDED"
            list_corpus[idx] = ans
        if isinstance(ans, str):
            list_corpus[idx] = unicode(ans, 'utf-8')
#	elif isinstance(ans, unicode):
#   		list_corpus[idx] = ans.encode('ascii', 'ignore')


def preprocess_data(X_train):
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

    stop_words = stopwords.words('english')
    stop_words.sort()

    #stemmer = PorterStemmer()

    for i in range(len(X_train)):
        ans = X_train[i]
        words = word_tokenize(ans)
        wordsFiltered = []
        for w in words:
            if w not in stop_words:
                wordsFiltered.append(Word(w).lemmatize())

        ans = ' '.join(word for word in wordsFiltered)
        X_train[i] = ans
    return X_train


def tfidf(X_train, X_test):
    vectorizer = TfidfVectorizer(
        stop_words="english", analyzer='word', ngram_range=(1, 3))
    train_vectors = vectorizer.fit_transform(X_train)
    test_vectors = vectorizer.transform(X_test)
    return vectorizer, train_vectors, test_vectors


def naive_bayes(train_vectors, y_train, test_vectors):
    nb = MultinomialNB(alpha=.01)
    nb.fit(train_vectors, y_train)
    y_pred = nb.predict(test_vectors)
    return nb, y_pred


def sorted_features(vectorizer, nb):
    class_zero_prob_sorted = nb.feature_log_prob_[0, :].argsort()
    class_one_prob_sorted = nb.feature_log_prob_[1, :].argsort()
    class_two_prob_sorted = nb.feature_log_prob_[2, :].argsort()

    zero = np.take(vectorizer.get_feature_names(), class_zero_prob_sorted[:-1])
    one = np.take(vectorizer.get_feature_names(), class_one_prob_sorted[:-1])
    two = np.take(vectorizer.get_feature_names(), class_two_prob_sorted[:-1])

    return zero, one, two


def learn():
    global X_train, X_test, y_train, y_pred, zero, one, two
    X_train = preprocess_data(X_train)
    vectorizer, train_vectors, test_vectors = tfidf(X_train, X_test)
    nb, y_pred = naive_bayes(train_vectors, y_train, test_vectors)
    zero, one, two = sorted_features(vectorizer, nb)


def update_phrase_exp(item, trig_tok, list_, phrase_list):
    for phrase in list_:
        phrase_tok = nltk.word_tokenize(phrase)
        tok_len = len(trig_tok)
        phrase_len = len(phrase_tok)

        if tok_len == phrase_len and \
                trig_tok[0] == phrase_tok[0] and \
                item not in phrase_list:
            phrase_list.append(item)
    return phrase_list


def generate_explanation(test_idx):
        # TODO : modify to make case insensitiv checks
    global zero_phrases, one_phrases, two_phrases, X_test, y_pred, zero, one, two
    pred = y_pred[test_idx]
    tokens = nltk.word_tokenize(X_test[test_idx])

    bigram_tuples = list(nltk.bigrams(tokens))
    bigrams = []
    for a, b in bigram_tuples:
        bigram = ' '.join((a, b))
        bigrams.append(str(bigram))

    trigram_tuples = list(nltk.trigrams(tokens))
    trigrams = []
    for a, b, c in trigram_tuples:
        if c != '.':
            trigram = ' '.join((a, b, c))
        else:
            b = ''.join((b, c))
            bigram = ' '.join((a, b))
            bigrams.append(str(bigram))
        trigrams.append(str(trigram))

    zero_phrases = []
    one_phrases = []
    two_phrases = []

    #zero = map(str, zero)
    #one = map(str, one)
    #two = map(str, two)

    for item in bigrams:
        if item in zero:
            zero_phrases.append(item)
        elif item in one:
            one_phrases.append(item)
        elif item in two:
            two_phrases.append(item)

    for item in trigrams:
        if item in zero:
            zero_phrases.append(item)
        elif item in one:
            one_phrases.append(item)
        elif item in two:
            two_phrases.append(item)
        else:
            trig_tok = nltk.word_tokenize(item)
            if pred == '0' or pred == 0:
                list_ = zero
                zero_phrases = update_phrase_exp(item, trig_tok,
                                                 list_, zero_phrases)
            elif pred == '1' or pred == 1:
                list_ = one
                one_phrases = update_phrase_exp(item, trig_tok,
                                                list_, one_phrases)
            else:
                list_ = two
                two_phrases = update_phrase_exp(item, trig_tok,
                                                list_, two_phrases)

                # Also update the tfidf list
    for item in tokens:
        if item in zero:
            zero_phrases.append(item)
        elif item in one:
            one_phrases.append(item)
        elif item in two:
            two_phrases.append(item)

    return zero_phrases, one_phrases, two_phrases


def remove_duplicate_phrases(phrase_list):
    unigrams = []
    bigrams = []
    trigrams = []

    for item in phrase_list:
        tokens = nltk.word_tokenize(item)
        length = len(tokens)

        if length == 2:
            bigrams.append(item)
        elif length == 3:
            trigrams.append(item)

    # remove duplicate unigrams in phrase list that is also in bigrams
    for bigram in bigrams:
        bigr_tokens = nltk.word_tokenize(bigram)
        for tok in bigr_tokens:
            phrase_list[:] = (value for value in phrase_list if value != tok)

    # remove duplicate unigrams and bigrams in phrase list that is also in trigrams
    for trigram in trigrams:
        trig_tokens = nltk.word_tokenize(trigram)
        for trig_tok in trig_tokens:
            phrase_list[:] = (
                value for value in phrase_list if value != trig_tok)

        bigram_tuples = list(nltk.bigrams(trig_tokens))

        for a, b in bigram_tuples:
            bigram = ' '.join((a, b))
            bigram = str(bigram)
            phrase_list[:] = (
                value for value in phrase_list if value != bigram)

    return phrase_list


def mark_words(x_test, predicted_phrases, pred_tags, non_pred_phrases):
    for phrase in predicted_phrases:
        highlighted_phrase = pred_tags[0]+phrase+pred_tags[1]
        x_test = x_test.replace(phrase, highlighted_phrase)
    #if non_pred_tag is not None:
    #    for phrase in non_pred_phrases:
    #        if phrase not in predicted_phrases:
    #            highlighted_phrase = non_pred_tag[0]+phrase+non_pred_tag[1]
    #            x_test = x_test.replace(phrase, highlighted_phrase)
    # for phrase in non_pred_phrases[1]:
    #    if phrase not in predicted_phrases:
    #        highlighted_phrase = non_pred_tag2[0]+phrase+non_pred_tag2[1]
    #        x_test = x_test.replace(phrase,highlighted_phrase)
    return x_test


def as_html_op(x_test, y_pred, feedback=False):
    global zero_phrases, one_phrases, two_phrases, saved_expl

    ans = ""+x_test
    zero_mark_tags = ['<mark style="background-color:#FFAB91;\">', '</mark>']
    one_mark_tags = ['<mark style="background-color:#F9E79F;\">', '</mark>']
    two_mark_tags = ['<mark style="background-color:#E6EE9C;\">', '</mark>']

    #non_pred_phrases = []

    # TODO :Mark stopwords in white
    if y_pred == '0' or y_pred == 0:
        # non_pred_phrases.append(one_phrases)
        # non_pred_phrases.append(two_phrases)
        #x_test = mark_words(x_test, zero_phrases, zero_mark_tags, non_pred_phrases, one_mark_tags, two_mark_tags)
        x_test = mark_words(x_test, zero_phrases,
                            zero_mark_tags, one_phrases, one_mark_tags)

    if y_pred == '1' or y_pred == 1:
        # non_pred_phrases.append(zero_phrases)
        # non_pred_phrases.append(two_phrases)
        #x_test = mark_words(x_test, one_phrases, one_mark_tags, non_pred_phrases, zero_mark_tags, two_mark_tags)
        x_test = mark_words(x_test, one_phrases, one_mark_tags, None)

    if y_pred == '2' or y_pred == 2:
        # non_pred_phrases.append(zero_phrases)
        # non_pred_phrases.append(one_phrases)
        #x_test = mark_words(x_test, two_phrases, two_mark_tags, non_pred_phrases, one_mark_tags, zero_mark_tags)
        x_test = mark_words(x_test, two_phrases, two_mark_tags, None)

    saved_expl[ans] = x_test

    return x_test


def correction_after_feedback(feedback_zero, feedback_one, feedback_two):
    global zero_phrases, one_phrases, two_phrases, vocab_zero, vocab_one, vocab_two
    for phrase in feedback_zero:
        if phrase not in zero_phrases:
            zero_phrases.append(phrase)

    for phrase in feedback_one:
        if phrase not in one_phrases:
            one_phrases.append(phrase)

    for phrase in feedback_two:
        if phrase not in two_phrases:
            two_phrases.append(phrase)

# This following code is tentative
#        for phrase in vocab_zero:
#            if phrase in one_phrases:
#                one_phrases.remove(phrase)
#            if phrase in two_phrases:
#                one_phrases.remove(phrase)

#        for phrase in vocab_incorr:
#            if phrase in zero_phrases:
#                zero_phrases.remove(phrase)
    return zero_phrases, one_phrases, two_phrases


def grade_and_explain(feedback):
    global zero_phrases, one_phrases, two_phrases, X_test, y_pred
    global html_out, pred, vocab_zero, vocab_one, vocab_two
    global saved_grades

    learn()
    idx = 0
    pred = y_pred[idx]
    x_test = X_test[idx]
    zero_phrases, one_phrases, two_phrases = generate_explanation(idx)

    zero_phrases = remove_duplicate_phrases(zero_phrases)
    one_phrases = remove_duplicate_phrases(one_phrases)
    two_phrases = remove_duplicate_phrases(two_phrases)
    saved_grades[x_test] = pred

    if feedback == 'False':
        html_out = Markup(as_html_op(x_test, pred))
    else:
        for phrase in vocab_zero:
            if phrase not in zero_phrases:
                zero_phrases.append(phrase)

        for phrase in vocab_one:
            if phrase not in one_phrases:
                one_phrases.append(phrase)

        for phrase in vocab_two:
            if phrase not in two_phrases:
                two_phrases.append(phrase)
        html_out = Markup(as_html_op(x_test, pred))

    return pred, html_out


def integrate_in_jupyter(csv_file):
    global dataset_name, dataset_path, exam_name
    data = pd.read_csv(csv_file)
    list_student_id = data["student_id"].tolist()
    list_answers = data["answers"].tolist()
    list_points = data["points"].tolist()
    list_expls = data["explanations"].tolist()

    for idx in range(len(list_student_id)):
        student_id = list_student_id[idx]
        answer = list_answers[idx]
        grade = list_points[idx]
        explanation = list_expls[idx]
        path_to_ipynb, ipynb_file = get_ipynb_file(
            dataset_path, student_id, exam_name)

        output_path = './outputs/'+dataset_name + \
            '/'+str(student_id)+'/'+exam_name+'/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        output_file = os.path.join(output_path, ipynb_file)
        output_file_exists = os.path.isfile(output_file)
        file_to_read = ""
        if output_file_exists:
            file_to_read = output_file
        else:
            file_to_read = path_to_ipynb + ipynb_file

        with open(file_to_read, 'r') as json_file:
            data = json.load(json_file)
            for (index, cell) in enumerate(data['cells']):
                if 'nbgrader' in cell['metadata'] and cell['metadata']['nbgrader']['solution'] == True:
                    solution_in_cell = ''
                    for string in cell['source']:
                        solution_in_cell = solution_in_cell+string
                    if solution_in_cell == answer:  # also check if checksum matches if possible
                        cell['metadata']['nbgrader']['points'] = int(grade)
                        if explanation != "NA":
                            cell['source'] = explanation
                        else:
                            cell['source'] = answer
                        break
                    else:
                        continue

        with open(output_file,  'w') as json_file:
            json_file.write(json.dumps(data))
    return


############################################################################
data, list_corpus, list_labels, questions = ([] for i in range(4))

X_train, X_test, y_train, y_test, stud_ans = ([] for i in range(5))
scores, vocab_zero, vocab_one, vocab_two, true_grades, qlist = (
    [] for i in range(6))
input_filename, ques, question, pred, html_out = ["" for i in range(5)]
current_ans, dataset_name, dataset_path, exam_name = ["" for i in range(4)]
saved_expl, saved_grades = [{} for i in range(2)]

total_questions = 0
total_students = 0
total_answers = 31
ans_num = 1
directory = './data/csv/'
selected = 'False'
upload_status = 'False'
model_answers = dict()
model_ans = "Model answer not provided."
end = None
DEFAULT_ANS = "YOUR ANSWER HERE"
DEFAULT_SCORE = "0"
DUMMY_ANS = "DUMMY ANS FOR 1 P"
DUMMY_ANS_SCORE = "1"
############################################################################


def init_application(dataset_path, student_ids, exam_name_lst):
    global qlist, qlist, directory, data, list_corpus, list_labels
    global questions, question, X_train, X_test, y_train, y_test, stud_ans
    global upload_status, total_answers, input_filename
    qlist, unique_questions = jupyter_to_csv(
        dataset_path, student_ids, exam_name_lst)
    ques = qlist[0]

    input_filename = ques+".csv"
    data, list_corpus, list_labels = read_csv(directory+ques+".csv")
    total_answers = len(list_corpus)
    questions = data["question"].unique().tolist()
    question = questions[0]

    X_train, X_test, y_train, y_test = train_test_split(list_corpus,
                                                        list_labels,
                                                        test_size=0.60,
                                                        random_state=40)
    y_train = []
    for idx in range(len(X_train)):
        stud_ans.append(X_train[idx])

    num_of_questions = len(unique_questions)
    return num_of_questions


@app.route('/')
def index():
    global upload_status
    upload_status = 'False'
    return render_template('file_upload.html',
                           upload_status=upload_status)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global upload_status, dataset_name, dataset_path, exam_name
    global total_students, total_questions

    if request.method == 'POST':
        if 'data_file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['data_file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path_to_zip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            zf = ZipFile(path_to_zip, 'r')
            zf.extractall('./data/uploads/')
            zf.close()
            os.remove(path_to_zip)

        dataset_names = os.listdir('./data/uploads/')
        dataset_entries = []
        dataset_path = ""
        for name in dataset_names:
            dataset_name = name
            dataset_path = os.path.join(
                os.path.abspath('./data/uploads/'), dataset_name)
            if os.path.isdir(dataset_path):
                dataset_entries = os.listdir(dataset_path)

        student_ids = []
        exam_name_lst = ""
        for entry in dataset_entries:
            id_path = os.path.join(os.path.abspath(dataset_path), entry)
            if os.path.isdir(id_path):
                total_students = total_students + 1
                student_ids.append(entry)
                exam_name_lst = os.listdir(id_path)

        total_questions = init_application(
            dataset_path, student_ids, exam_name_lst)
        upload_status = 'True'
        return render_template('file_upload.html',
                               upload_status=upload_status,
                               total_students=total_students,
                               total_questions=total_questions)


@app.route('/model', methods=['GET', 'POST'])
def read_model_ans():
    global model_ans, model_answers, upload_status, total_students, total_questions
    filename = ""
    model_ans_status = "False"
    if request.method == 'POST':
        if 'model_ans' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['model_ans']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        model_answers = get_model_answers('./data/uploads/'+filename)
        if len(model_answers) > 0:
            model_ans_status = "True"
        return render_template('file_upload.html',
                               upload_status=upload_status,
                               total_students=total_students,
                               total_questions=total_questions,
                               model_ans_status=model_ans_status)


@app.route('/start', methods=['GET', 'POST'])
def start():
    global stud_ans, current_ans, total_answers, ans_num, model_answers, model_ans
    current_ans = ""
    current_ans = current_ans+stud_ans[0]
    stud_ans.remove(current_ans)
    if len(model_answers) > 0:
        model_ans = model_answers["Question_1"]
    return render_template('index.html',
                           current_ans=current_ans,
                           qlist=qlist,
                           question=question,
                           model_ans=model_ans,
                           total_answers=total_answers,
                           ans_num=ans_num,
                           selected=selected)


@app.route('/new', methods=['GET', 'POST'])
def new():
    global stud_ans, directory, data, list_corpus, list_labels, current_ans, ans_num
    global X_train, X_test, y_train, y_test, saved_expl, saved_grades, total_answers
    global selected, qlist, ques, question, model_answers, model_ans, question_filenames, input_filename

    if request.method == "POST":
        # Get the question number selected
        ques = request.form['question']
        #ques_file = question_filenames[ques]

        input_filename = ques+".csv"
        filepath = directory+input_filename
        data, list_corpus, list_labels = read_csv(filepath)
        total_answers = len(list_corpus)
        # safe_strings()

        questions = data["question"].unique().tolist()
        question = questions[0]

        X_train, X_test, y_train, y_test = train_test_split(list_corpus,
                                                            list_labels,
                                                            test_size=0.60,
                                                            random_state=40)
        saved_expl = {}
        saved_grades = {}
        stud_ans = []
        y_train = []
        for idx in range(len(X_train)):
            stud_ans.append(X_train[idx])
        #question = questions[ques]
        if len(model_answers) > 0:
            model_ans = model_answers[ques]
        else:
            model_ans = "Model answer not provided."
        current_ans = ""
        current_ans = current_ans+stud_ans[0]
        stud_ans.remove(current_ans)
        selected = 'True'
        return render_template('index.html', current_ans=current_ans,
                               qlist=qlist,
                               ques=ques,
                               question=question,
                               model_ans=model_ans,
                               total_answers=total_answers,
                               ans_num=ans_num,
                               selected=selected)


@app.route("/grading", methods=['GET', 'POST'])
def grading():
    global stud_ans, scores, X_train, X_test, y_train, total_answers
    global selected, qlist, ques, question, model_ans, current_ans
    global saved_grades, saved_expl, feedback, ans_num

    feedback = "False"
    ans = ""

    grade = request.form.get('grade', None)
    if grade is None:
        if stud_ans[0] != "YOUR ANSWER HERE" and stud_ans[0] != "NO ANSWER PROVIDED":
            grade = '1'
        else:
            grade = '0'
    scores.append(grade)
    y_train.append(grade)
    saved_expl[current_ans] = "NA"
    saved_grades[current_ans] = grade

    if len(stud_ans) > 0:
        current_ans = ""
        current_ans = current_ans+stud_ans[0]
        stud_ans.remove(current_ans)
    else:
        X_train.append(DEFAULT_ANS)
        X_train.append(DUMMY_ANS)
        y_train.append(DEFAULT_SCORE)
        y_train.append(DUMMY_ANS_SCORE)
        pred, html_out = grade_and_explain(feedback)
        ans_num = ans_num+1
        print(html_out)
        print("\n")
        return render_template('autograde.html', html_out=html_out,
                               pred=pred,
                               feedback=feedback,
                               qlist=qlist,
                               ques=ques,
                               question=question,
                               model_ans=model_ans,
                               total_answers=total_answers,
                               ans_num=ans_num,
                               selected=selected)

    if request.method == "POST":
        ans_num = ans_num+1
        return render_template('index.html', current_ans=current_ans,
                               qlist=qlist,
                               ques=ques,
                               question=question,
                               model_ans=model_ans,
                               total_answers=total_answers,
                               ans_num=ans_num,
                               selected=selected)


@app.route("/feedback", methods=['GET', 'POST'])
def handle_feedback():
    global zero_phrases, one_phrases, two_phrases, y_pred, X_test
    global vocab_zero, vocab_one, vocab_two, html_out, pred, ans_num
    global selected, qlist, ques, question, model_ans, total_answers
    global true_grades, feedback_green, feedback_red, end, feedback

    human_label = request.form.get('new_points', None)
    feedback_zero = request.form['f_zero']
    feedback_one = request.form['f_one']
    feedback_two = request.form['f_two']

    if not human_label:
        true_pred = y_pred[0]
    else:
        true_pred = human_label

    true_grades.append(true_pred)

    if not feedback_zero:
        print("No correction for red phrases provided for this answer")
    else:
        feedback_zero = [x.strip() for x in feedback_zero.split(",")]

    if not feedback_one:
        print("No correction for yellow phrases provided for this answer")
    else:
        feedback_one = [x.strip() for x in feedback_one.split(",")]

    if not feedback_two:
        print("No correction for green phrases provided for this answer")
    else:
        feedback_two = [x.strip() for x in feedback_two.split(",")]

    for phrase in feedback_zero:
        if phrase != "":
            vocab_zero.append(phrase)

    for phrase in feedback_one:
        if phrase != "":
            vocab_one.append(phrase)

    for phrase in feedback_two:
        if phrase != "":
            vocab_two.append(phrase)

    zero_phrases, one_phrases, two_phrases = correction_after_feedback(
        feedback_zero, feedback_one, feedback_two)

    # if end=="End":
    #	create_output_csv()

    if request.method == "POST":
        x_test = X_test[0]
        pred = true_pred
        saved_grades[x_test] = pred
        html_out = Markup(as_html_op(x_test, y_pred[0]))
        feedback_zero = ', '.join(feedback_zero)
        feedback_one = ', '.join(feedback_one)
        feedback_two = ', '.join(feedback_two)
        y_pred[0] = pred
        feedback = "True"
        return render_template('autograde.html', html_out=html_out,
                               pred=pred,
                               human_label=human_label,
                               feedback_zero=feedback_zero,
                               feedback_one=feedback_one,
                               feedback_two=feedback_two,
                               feedback=feedback,
                               qlist=qlist,
                               ques=ques,
                               question=question,
                               model_ans=model_ans,
                               total_answers=total_answers,
                               ans_num=ans_num,
                               selected=selected)


@app.route("/next", methods=['GET', 'POST'])
def postfeedback():
    global zero_phrases, one_phrases, two_phrases, X_train, y_train, X_test, y_pred
    global vocab_zero, vocab_one, vocab_two, html_out, pred
    global selected, qlist, ques, question, model_ans, total_answers
    global saved_ans, given_grades, end, feedback, ans_num

    end = None
    saved = None
    feedback = "True"
    if len(X_test) > 1:
        x_test = X_test[0]
        X_train.append(x_test)
        y_train.append(y_pred[0])
        X_test.remove(x_test)

        if len(X_test) == 1:
            end = "End"

        pred, html_out = grade_and_explain(feedback)

        for phrase in vocab_zero:
            if phrase not in zero_phrases:
                zero_phrases.append(phrase)

        for phrase in vocab_one:
            if phrase not in one_phrases:
                one_phrases.append(phrase)

        for phrase in vocab_two:
            if phrase not in two_phrases:
                two_phrases.append(phrase)
    else:
        end = "End"

    if request.method == "POST":
        feedback = "False"
        ans_num = ans_num+1
        return render_template('autograde.html', html_out=html_out,
                               pred=pred,
                               feedback=feedback,
                               end=end,
                               saved=saved,
                               qlist=qlist,
                               ques=ques,
                               question=question,
                               model_ans=model_ans,
                               total_answers=total_answers,
                               ans_num=ans_num,
                               selected=selected)


@app.route("/save", methods=['GET', 'POST'])
def create_output_csv():
    global data, input_filename, list_corpus, saved_grades, saved_expl
    global html_out, pred, selected, qlist, ques, question, model_ans
    global saved_ans, given_grades, end, feedback, total_answers, ans_num

    id_for_ans = data['student_id'].tolist()
    ques_num = data['question_number'].tolist()
    ques = []
    answers = []
    grades_given = []
    explanations = []
    for idx in range(len(list_corpus)):
        ans = list_corpus[idx]
        ques.insert(idx, question)
        answers.insert(idx, ans)
        grades_given.insert(idx, saved_grades[ans])
        explanations.insert(idx, saved_expl[ans])

    output = {'student_id': id_for_ans,
              'question_number': ques_num,
              'question': ques,
              'answers':  answers,
              'points': grades_given,
              'explanations':  explanations}

    df = DataFrame(output, columns=[
                   'student_id', 'question_number', 'question', 'answers', 'points', 'explanations'])

    OUTPUT_CSV_DIR = './outputs/csv/'
    if not os.path.exists(OUTPUT_CSV_DIR):
        os.makedirs(OUTPUT_CSV_DIR)
    output_file = OUTPUT_CSV_DIR+input_filename
    df.to_csv(output_file, encoding='utf-8')

    integrate_in_jupyter(output_file)

    return render_template('autograde.html', html_out=html_out,
                           pred=pred,
                           feedback=feedback,
                           end=end,
                           saved="saved",
                           qlist=qlist,
                           ques=ques,
                           question=question,
                           model_ans=model_ans,
                           total_answers=total_answers,
                           ans_num=ans_num,
                           selected=selected)


if __name__ == '__main__':
    app.run(debug=True)
