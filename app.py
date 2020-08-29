from flask import Flask, render_template, flash, request, Markup
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

# App config.
DEBUG = True
app = Flask(__name__, template_folder='templates')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# Matching tense with color
def tense2color(tense):
    if tense == 'Past Simple':
        return "#00B8FF"

    if tense == 'Past Progressive':
        return "#A75EFF"

    if tense == 'Past Perfect Simple':
        return "#0029BB"

    if tense == 'Present Simple':
        return "#00B8B4"

    if tense == 'Present Progressive':
        return "#00FFF9"

    if tense == 'Future Simple':
        return "#00FF89"

    if tense == 'Future Progressive':
        return '#00FF11'

    return 'grey'

# Convert tagged word list into string
# Identify tense and return the color correspoding to the tense
# Add the result to analyzed list
past_simple = False
present_simple = False
future_simple = False
def findTense(analyzed_list, tagged):
    # Convert tagged word list into string
    global past_simple
    global present_simple
    global future_simple

    button_text = ''
    for word_tag in tagged:
        if word_tag[0].isalpha():
            button_text += ' ' + word_tag[0]
        else:
            button_text += word_tag[0]

    if past_simple == True:
        if tagged[0][1] == 'VBG':
            tense = 'Past Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)

        else:
            tense = 'Past Simple'
            color_name = tense2color(tense)
            if tagged[0][1] == 'VBN':
                voice = "Passive"
            else:
                voice = 'Active'

        past_simple = False
        return [button_text[1:], True, color_name, tense, voice]

    if present_simple == True:
        if tagged[0][1] == 'VBG':
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)

        else:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            if tagged[0][1] == 'VBN':
                voice = "Passive"
            else:
                voice = 'Active'

        present_simple = False
        return [button_text[1:], True, color_name, tense, voice]

    if future_simple == True:
        tense = 'Future Simple'
        voice = 'Active'
        if len(tagged) > 1 and tagged[0][0] == 'be':
            if tagged[1][1] == 'VBG':
                tense = 'Future Progressive'
                changeTense(analyzed_list, tense)
            elif tagged[1][1] == 'VBN':
                voice = 'Passive'

        color_name = tense2color(tense)
        future_simple = False
        return [button_text[1:], True, color_name, tense, voice]

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
            if tagged[0][0] in ["did", "Did", "was", "Was", "were", "Were"]:
                past_simple = True

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            if tagged[0][0] in ['do', "Do", "does", "Does", "is", "Is", "are", "Are", "'s", "'re"]:
                present_simple = True

        elif tagged[0][0] in ['can', 'Can']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            present_simple = True

        elif tagged[0][1] == 'VBG':
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice ='Active' 

        elif tagged[0][0] in ['will', "Will", "'ll"]:
            tense = "Future Simple"
            color_name = tense2color(tense)
            voice = 'Active'
            future_simple = True

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

        elif tagged[1][0] in ["not", "n't"]:
            if tagged[0][1] in ['VB', 'VBP', 'VBZ']:
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice ='Active'
            if tagged[0][1] in ['VBD', 'VBN']:
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

        elif tagged[0][1] == 'MD' and tagged[0][0] not in ['will', 'Will']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][0] in ["am", "Am","is", "Is", "are", "Are", "'s", "'re", "'m"] and tagged[1][1] == 'VBG':
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice = 'Active'

        elif tagged[0][0] in ['will', 'Will'] and tagged[1][1] == 'VB':
            tense = 'Future Simple'
            color_name = tense2color(tense)
            voice ='Active'

    elif len(tagged) == 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][1] == 'VBD':
                if tagged[2][1] in ['VB', 'VBP']:
                    tense = 'Past Simple'
                    color_name = tense2color(tense)
                    voice ='Active' 

                elif tagged[2][1] in ['VBD', 'VBN']:
                    tense = 'Past Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

                elif tagged[2][1] == 'VBG':
                    tense = 'Past Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[0][0] in ["could", "Could"]:
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
                if tagged[2][1] in ['VB', 'VBP']:
                    tense = 'Present Simple'
                    color_name = tense2color(tense)
                    voice ='Active'

                elif tagged[2][1] in ['VBD', 'VBN']:
                    tense = 'Present Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

                elif tagged[2][1] == 'VBG':
                    tense = 'Present Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[0][0] in ['ca', 'Ca']:
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[0][0] in ['will', 'Will', 'wo', 'Wo']:
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice ='Active'

        elif tagged[0][0] in ["will", "Will"]:
            if tagged[1][0] == "be":
                if tagged[2][1] == 'VBG':
                    tense = 'Future Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

                elif tagged[2][1] == 'VBN':
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'

    elif len(tagged) > 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][0] in ['will', 'Will', 'wo', 'Wo']:
                if tagged[2][0] == 'be' and tagged[3][1] == 'VBN':
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

    return [button_text[1:], True, color_name, tense, voice]

def allFlag2False():
    global past_simple
    past_simple = False

    global present_simple
    present_simple = False

def changeTense(analyzed_list,tense):
    for i in reversed(analyzed_list):
        if i[1]:
            i[3] = tense
            i[2] = tense2color(tense)
            break

def changeVoice(analyzed_list, voice):
    for i in reversed(analyzed_list):
        if i[1]:
            i[4] = voice
        break

def analyze_text(story):
    analyzed = [] # Form (word, isVerb, color, tense, voice)
    paragraphs = story.split('\n') # Split into paragraphs
    for p in paragraphs:
        token = nltk.word_tokenize(p)
        tagged = nltk.pos_tag(token)
        print(tagged)

        button_tagged = []
        for word_tag in tagged:
            if word_tag[1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD'] or word_tag[0] in ["not", "Not", "n't"]:
                button_tagged.append(word_tag)
            else:
                if button_tagged:
                    # button_text, tense, color_name, detail = findTense(button_tagged)
                    analyzed.append(findTense(analyzed, button_tagged))
                    button_tagged.clear()

                if word_tag[0].isalpha():
                    analyzed_word = [word_tag[0], False, None, None, None]
                    analyzed.append(analyzed_word)
                else:
                    analyzed_not_word = [word_tag[0], None, None, None, None]
                    analyzed.append(analyzed_not_word)
                    if word_tag[0] in [".", "!", "?"]:
                        allFlag2False()


        analyzed_break_line = (Markup('<br>'), None, None, None, None)
        analyzed.append(analyzed_break_line)

    return analyzed


class Form(Form):
    @app.route("/", methods=['GET', 'POST'])
    def main():
        analyzed = None
        story = request.args.get('story')
        if story is not None:
            analyzed = analyze_text(story)

        color_annotate = [['Past Simple', tense2color('Past Simple')], 
                            ['Past Progressive', tense2color('Past Progressive')],
                            ['Past Perfect Simple', tense2color('Past Perfect Simple')],
                            ['Present Simple', tense2color('Present Simple')],
                            ['Present Progressive', tense2color('Present Progressive')],
                            ['Future Simple', tense2color('Future Simple')],
                            ['Future Progressive', tense2color('Future Progressive')]]

        detail = None
        detail = request.args.get('detail-btn')
        if detail is not None:
            detail = detail.split(';')
            flash("Tense: " + detail[0])
            flash("Voice: " + detail[1])
            detail = None

        return render_template('home.html',story = story, analyzed = analyzed, color_annotate = color_annotate)

if __name__ == "__main__":
    app.run()