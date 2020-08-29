from flask import Flask, render_template, flash, request, Markup
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# App config.
DEBUG = True
app = Flask(__name__, template_folder='templates')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


# Matching tense with color
def tense2color(tense):
    if tense == 'Past Simple':
        # return 'cornflower blue'
        return "#00B8FF"

    if tense == 'Past Progressive':
        # return 'medium slate blue'
        return "#7100FF"

    if tense == 'Past Perfect Simple':
        # return 'royal blue'
        return "#0029BB"

    if tense == 'Present Simple':
        # return 'turquoise'
        return "#00B8B4"

    if tense == 'Present Progressive':
        # return 'cyan'
        return "#00FFF9"

    if tense == 'Future Simple':
        # return 'pale green'
        return "#00FF89"

    return 'grey'

# Convert tagged word list into string
# Identify tense and return the color correspoding to the tense
def findTense(tagged):
    # Convert tagged word list into string
    button_text = ''
    for word_tag in tagged:
        button_text += ' ' + word_tag[0]

    # Identify tense
    tense = 'Unidentified'
    color_name = 'grey'
    voice = "Unidentified"
    detail = []
    if len(tagged) == 1:
        if tagged[0][1] == 'VBD':
            tense = 'Past Simple'
            color_name = tense2color(tense)
            voice = 'Active'

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][1] == 'VBG':
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice ='Active'

    elif len(tagged) == 2:
        if tagged[0][0] in ['was', 'were', 'Was', 'Were'] and tagged[1][1] == 'VBN':
            tense = 'Past Simple'
            color_name = tense2color(tense)
            voice ='Passive'

        if tagged[0][0] in ['was', 'were', 'Was', 'Were'] and tagged[1][1] == 'VBG':
            tense = 'Past Progressive'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][0] == 'had' and tagged[1][1] == 'VBN':
            tense = 'Past Perfect Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][1] == 'MD' and tagged[0][0] not in ['will', 'Will']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][0] in ['will', 'Will'] and tagged[1][1] == 'VB':
            tense = 'Future Simple'
            color_name = tense2color(tense)
            voice ='Active'

    elif len(tagged) == 3:
        if tagged[0][0] not in ['have', 'has', 'had', 'Have', 'Has', 'Had']:
            if tagged[0][1] == 'VBD':
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

    return button_text[1:], True, color_name, tense, voice

def analyze_text(story):
    analyzed = [] # Form (word, isVerb, color, tense, voice)
    paragraphs = story.split('\n') # Split into paragraphs
    for p in paragraphs:
        token = nltk.word_tokenize(p)
        tagged = nltk.pos_tag(token)
        print(tagged)

        button_tagged = []
        for word_tag in tagged:
            if word_tag[1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD'] or word_tag[0] in ['not', 'Not']:
                button_tagged.append(word_tag)
            else:
                if button_tagged:
                    # button_text, tense, color_name, detail = findTense(button_tagged)
                    analyzed.append(findTense(button_tagged))
                    button_tagged.clear()

                analyzed_not_verb = (word_tag[0], False, None, None, None)
                analyzed.append(analyzed_not_verb)

        analyzed_break_line = (Markup('<br>'), False, None, None, None)
        analyzed.append(analyzed_break_line)

    return analyzed


class Form(Form):
    @app.route("/", methods=['GET', 'POST'])
    def main():
        analyzed = None
        story = request.args.get('story')
        if story is not None:
            analyzed = analyze_text(story)

        detail = None
        detail = request.args.get('detail-btn')
        if detail is not None:
            detail = detail.split(';')
            flash("Tense: " + detail[0])
            flash("Voice: " + detail[1])
            detail = None

        return render_template('home.html',story = story, analyzed = analyzed)

if __name__ == "__main__":
    app.run()