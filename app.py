from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey
from surveys import surveys

SURVEY_ID = 'current_survey'
RESPONSES = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretKey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """ Choose Survey"""
    return render_template('home.html', surveys = surveys)

@app.route('/', methods=["POST"])
def survey_selected():
    current_survey = request.form.get('survey_code', '')
    session[SURVEY_ID] = current_survey
    survey = surveys.get(current_survey)

    session[RESPONSES] = []

    return render_template('/survey.html', survey = survey)

@app.route('/questions/<int:id>')
def questions(id):
    responses = session[RESPONSES]
    survey_id = session[SURVEY_ID]
    survey = surveys.get(survey_id)
    num_questions = len(survey.questions)

    if id is None:
        return redirect('/')
    elif len(responses) == num_questions:
        return redirect('/thank')
    elif id >= num_questions or id != len(responses):
        flash('Invalid question ID, please finish the current answer first', 'ID Error')
        return redirect(f'/questions/{len(responses)}')
    return render_template('questions.html', question = survey.questions[id], id = id)

@app.route('/answer', methods=["POST"])
def handle_answer():
    choice = request.form.get('answer')
    text = request.form.get('text', None)
    responses = session[RESPONSES]
    
    if choice == None:
        flash('Please enter your choice', 'Choice Missing')
        return redirect(f'/questions/{len(responses)}')
    elif text == '':
        flash('Please enter your Text', 'Text Missing')
        return redirect(f'/questions/{len(responses)}')       

    responses.append({"choice":choice, "text":text})
    session[RESPONSES] = responses
    
    return redirect(f'/questions/{len(responses)}')

@app.route('/thank')
def thank_page():
    survey_id = session[SURVEY_ID]
    survey = surveys[survey_id]
    responses = session[RESPONSES]

    return render_template('thank.html', questions = survey.questions, responses=responses)
