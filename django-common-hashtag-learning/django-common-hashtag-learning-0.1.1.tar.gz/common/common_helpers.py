from django.utils.crypto import get_random_string

P1_P3_YEARGROUP = ['P1', 'P2', 'P3']
P4_P7_YEARGROUP = ['P4', 'P5', 'P6', 'P7']
S1_S3_YEARGROUP = ['S1', 'S2', 'S3']
S4_S6_YEARGROUP = ['S4', 'S5', 'S6']

HGIOS_CATEGORIES = ['Leadership and management', 'Learning provision', 'Successes and achievements']

RESTRICT_CHARS = '0O1IlS5'

TRIAL_LENGTH = 28

"""
DELETE REQUEST SESSION VARS
Delete all of the session variables related to New Evaluation
"""
def delete_evaluation_request_session_vars(request):
    delete_session_variable(request, 'evaluation_head')
    delete_session_variable(request, 'evaluation_themes')
    delete_session_variable(request, 'evaluation_rated_themes')
    delete_session_variable(request, 'evaluation_rated_qis')

    delete_session_variable(request, 'has_teacher_evaluation')
    delete_session_variable(request, 'has_leader_evaluation')
    delete_session_variable(request, 'has_parent_evaluation')
    delete_session_variable(request, 'has_learner_evaluation')

    # Temp saved checked priorities - used when moving from New Evaluation Priorities to Add Custom Priorities
    delete_session_variable(request, 'selected_hgiours_priorities_keys')
    delete_session_variable(request, 'selected_teacher_priorities_keys')
    delete_session_variable(request, 'selected_leader_priorities_keys')
    delete_session_variable(request, 'selected_parent_priorities_keys')
    delete_session_variable(request, 'selected_learner_priorities_keys')

    delete_session_variable(request, 'teacher_evaluation_questions')
    delete_session_variable(request, 'leader_evaluation_questions')
    delete_session_variable(request, 'parent_evaluation_questions')
    delete_session_variable(request, 'learner_evaluation_questions')


def delete_survey_request_session_vars(request):
    delete_session_variable(request, 'priority_pk')
    delete_session_variable(request, 'survey_ratings')
    delete_session_variable(request, 'survey_class')


def delete_session_variable(request, session_key):

    try:
        del request.session[session_key]
    except KeyError:
        pass

def get_random_identifier(number_digits):

    # Create a random identifier but make sure it does not include characters which can be confused eg 0OI1lS5
    random_identifier = get_random_string(number_digits)

    # if any of the restrticted characters appear, create a new random identifier
    while any((rc in RESTRICT_CHARS) for rc in random_identifier):
        random_identifier = get_random_string(number_digits)

    return random_identifier

def get_dept_default_user_type(is_departmental):
    if is_departmental is True:
        return 'Teacher'
    else:
        return 'Leader'

def get_class_menu_choices(classes, required):
    line_split_classes = classes.splitlines()

    class_choices = []
    if required is True:
        class_choices.append(('No class', 'No class selected',))
    else:
        class_choices.append((0, 'All',))

    for class_num, survey_class in enumerate(line_split_classes):
        class_choices.append((class_num + 1, survey_class,))

    return class_choices


def get_tlight_colour(overall_rating):
    if overall_rating == 0:
        return 'tlight-grey'
    elif overall_rating > 2.33:
        return 'tlight-green'
    elif overall_rating > 1.66:
        return 'tlight-amber'
    else:
        return 'tlight-red'


def department_placeholders(text, faculty):
    return text.replace('{Department}', faculty.faculty_name)


def calc_overall_and_percentage_hgios_rating(rating_count, total_rating):
    if rating_count > 0:
        average_rating = total_rating / (rating_count * 6)
        percentage_rating = int(average_rating * 100)
        overall_rating = round(average_rating * 6, 2)
    else:
        overall_rating = 0
        percentage_rating = 0

    return {'percentage_rating': percentage_rating, 'overall_rating': overall_rating}

"""
GET AVERAGE ADJUSTED RAG
Return - an 'average' rating adjusted to sync RAG 1-3 with HGIOS 1-6
To keep the rating consistent with leader / teacher features, value should be between 1 and 6
So red (1) is 1, green (3) is 6, and amber (2) is 3.5
"""
def get_average_adjusted_rag(rated_questions):
    total = 0

    for question in rated_questions:
        total += (question.rating == 1) + (question.rating == 2) * 3.5 + (question.rating == 3) * 6

    # make sure there is at least one rated question before calculating adjusted_average
    if rated_questions.count() > 0:
        adjusted_average = total / rated_questions.count()
    else:
        adjusted_average = None

    return adjusted_average


def get_hgios_percentage(rating_score):
    if rating_score == 7:
        rating_score = 0
    rating_percent = int(rating_score / 6 * 100)
    return rating_percent

def get_bg_bar(overall_rating):
    if overall_rating > 5.15:
        return 'bg-excellent-bar'
    elif overall_rating > 4.32:
        return 'bg-very-good-bar'
    elif overall_rating > 3.49:
        return 'bg-good-bar'
    elif overall_rating > 2.66:
        return 'bg-satisfactory-bar'
    elif overall_rating > 1.83:
        return 'bg-weak-bar'
    else:
        return 'bg-unsatisfactory-bar'


"""
GET HGIOS SCALE RATING
Get the HGIOS rating based on a hgios score
Returns a rating Unsatisfactory through to Excellent (or Insufficient Data)
"""

def get_hgios_scale_rating(hgios_score):

    # this table can be tweaked to update cut-off rankings
    cut_offs = {
        'insufficient data': 1.0,
        'unsatisfactory': 1.25,
        'unsatisfactory-weak': 1.75,
        'weak': 2.25,
        'weak-satisfactory': 2.75,
        'satisfactory': 3.25,
        'satisfactory-good': 3.75,
        'good': 4.25,
        'good-very good': 4.75,
        'very good': 5.25,
        'very good-excellent': 5.75,
        'excellent': 6.0,
        'not rated': 7.0
    }

    hgios_scale_rating = None

    if hgios_score is None:
        hgios_scale_rating = 'Insufficient data'

    elif cut_offs.get('insufficient data') <= hgios_score < cut_offs.get('unsatisfactory'):
        hgios_scale_rating = 'Unsatisfactory'

    elif cut_offs.get('unsatisfactory') <= hgios_score < cut_offs.get('unsatisfactory-weak'):
        hgios_scale_rating = 'Unsatisfactory ➞ Weak'

    elif cut_offs.get('unsatisfactory-weak') <= hgios_score < cut_offs.get('weak'):
        hgios_scale_rating = 'Weak'

    elif cut_offs.get('weak') <= hgios_score < cut_offs.get('weak-satisfactory'):
        hgios_scale_rating = 'Weak ➞ Satisfactory'

    elif cut_offs.get('weak-satisfactory') <= hgios_score < cut_offs.get('satisfactory'):
        hgios_scale_rating = 'Satisfactory'

    elif cut_offs.get('satisfactory') <= hgios_score < cut_offs.get('satisfactory-good'):
        hgios_scale_rating = 'Satisfactory ➞ Good'

    elif cut_offs.get('satisfactory-good') <= hgios_score < cut_offs.get('good'):
        hgios_scale_rating = 'Good'

    elif cut_offs.get('good') <= hgios_score < cut_offs.get('good-very good'):
        hgios_scale_rating = 'Good ➞ Very good'

    elif cut_offs.get('good-very good') <= hgios_score < cut_offs.get('very good'):
        hgios_scale_rating = 'Very good'

    elif cut_offs.get('very good') <= hgios_score < cut_offs.get('very good-excellent'):
        hgios_scale_rating = 'Very good ➞ Excellent'

    elif cut_offs.get('very good-excellent') <= hgios_score <= cut_offs.get('excellent'):
        hgios_scale_rating = 'Excellent'

    elif hgios_score == cut_offs.get('not rated'):
        hgios_scale_rating = 'Not Rated'

    return hgios_scale_rating


# convert a year group to a stage
# e.g. 'S1' = 'S1-3', 'P4' = 'P4-7'
def get_stage(year_group):

    if year_group in S1_S3_YEARGROUP:
        stage = 'S1-3'
    elif year_group in S4_S6_YEARGROUP:
        stage = 'S4-6'
    elif year_group in P1_P3_YEARGROUP:
        stage = 'P1-3'
    else:
        stage = 'P4-7'

    return stage


# convert the year group choice into a list of possible year groups
# e.g. s1-3 = ['S1', 'S2', 'S3'] etc.
# if just a single year group convert it to a single item list
# e.g. p1 = ['P1']
def get_view_by_group_list(view_by_group):

    if view_by_group == 'all':
        view_by_group_list = P1_P3_YEARGROUP + P4_P7_YEARGROUP + S1_S3_YEARGROUP + S4_S6_YEARGROUP
    elif view_by_group == 'p1-7':
        view_by_group_list = P1_P3_YEARGROUP + P4_P7_YEARGROUP
    elif view_by_group =='p1-3':
        view_by_group_list = P1_P3_YEARGROUP
    elif view_by_group =='p4-7':
        view_by_group_list = P4_P7_YEARGROUP
    elif view_by_group == 's1-3':
        view_by_group_list = S1_S3_YEARGROUP
    elif view_by_group == 's4-6':
        view_by_group_list = S4_S6_YEARGROUP
    elif view_by_group == 's1-6':
        view_by_group_list = S1_S3_YEARGROUP + S4_S6_YEARGROUP
    else:
        view_by_group_list = view_by_group.upper().split()

    return view_by_group_list


def is_evaluation_departmental(evaluation):
    return evaluation.faculty.faculty_name != 'School'

def get_school_dept_word(is_departmental):
    if is_departmental is False:
        return 'school'
    else:
        return 'Department'


def get_school_dept_name(evaluation, is_departmental, preword):
    if is_departmental is False:
        return evaluation.school.school_name
    else:
        return preword + ' ' + evaluation.faculty.faculty_name + ' Department'


def get_progress_bar_percentage(numerator, denominator):

    if numerator is None:
        numerator = 0

    return str(int(numerator / denominator * 100)) + '%'


def get_rating_with_hgios_scale(rating_score):
    rating_text = get_hgios_scale_rating(rating_score)
    rating = str(rating_score) + ' - ' + rating_text

    return rating


def remove_false_dictionary_values(dictionary):
    return {key: val for key, val in dictionary.items() if val is not False}

def delete_evidence_request_session_vars(request):
    delete_session_variable(request, 'evidence_status')