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
        return '#00B8FF'

    if tense == 'Past Progressive':
        return '#0073FF'

    if tense == 'Past Perfect Simple':
        return '#7684B8'

    if tense == 'Past Perfect Progressive':
        return '#8C88EB'

    if tense == 'Present Simple':
        return '#A3FFFD'

    if tense == 'Present Progressive':
        return '#00FFF9'

    if tense == 'Present Perfect Simple':
        return '#71A6A8'

    if tense == 'Present Perfect Progressive':
        return '#36E0D8'

    if tense == 'Future Simple':
        return '#00FF89'

    if tense == 'Future Progressive':
        return '#00FF11'

    if tense == 'Future Perfect Simple':
        return '#54B868'

    if tense == 'Future Perfect Progressive':
        return '#A5E6B2'

    return 'grey'

# Convert tagged word list into string
# Identify tense and return the color correspoding to the tense
# Add the result to analyzed list
past_simple = False
past_perfect = False
present_simple = False
present_perfect = False
future_simple = False
future_perfect = False
flag_and = False
flag_get = False
previous = None
def findTense(analyzed_list, tagged):
    # Convert tagged word list into string
    global past_simple
    global present_simple
    global present_perfect
    global future_simple
    global past_perfect
    global future_perfect
    global flag_and
    global flag_get
    global previous

    button_text = ''
    for word_tag in tagged:
        if word_tag[0].isalpha():
            button_text += ' ' + word_tag[0]
        else:
            button_text += word_tag[0]

    if flag_and == True:
        if tagged[0][1] == 'VBG' and previous[3] in ['Past Progressive', 'Preset Progressive', 'Future Progressive']:
            tense = previous[3]
            color_name = tense2color(tense)
            voice = previous[4]
            return [button_text[1:], True, color_name, tense, voice]
        if tagged[0][1] in ['VBN'] and (previous[3] in ['Past Perfect Simple', 'Present Perfect Simple', 'Future Perfect Simple'] or previous[4] == 'Passive'):
            tense = previous[3]
            color_name = tense2color(tense)
            voice = previous[4]
            return [button_text[1:], True, color_name, tense, voice]

    if flag_get == True:
        if tagged[0][1] == 'VBN':
            tense = previous[3]
            color_name = tense2color(tense)
            voice = previous[4]
            return [button_text[1:], True, color_name, tense, voice]
        else:
            flag_get = False

    if tagged[-1][0] in ["get", "Get", "got", "Got"]:
        flag_get = True

    if past_simple == True:
        past_simple = False
        if tagged[0][1] == 'VBG':
            tense = 'Past Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]
            
        if tagged[0][1] == 'VBN':
            tense = 'Past Simple'
            color_name = tense2color(tense)
            voice = "Passive"
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]


    if past_perfect == True:
        past_perfect = False
        if tagged[0][1] == 'VBN':
            tense = 'Past Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]

    if present_simple == True:
        present_simple = False
        if tagged[0][1] == 'VBG':
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]

        if tagged[0][1] == 'VBN':
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice = "Passive"
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]

    if present_perfect == True:
        present_perfect = False

        if len(tagged) == 1 and tagged[0][1] == 'VBN':
            tense = 'Present Perfect Simple'
            color_name = tense2color(tense)
            changeTense(analyzed_list, tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        if len(tagged) > 1 and tagged[0][0] == "been" and tagged[1][1] == 'VBG':
            tense = 'Present Perfect Progressive'
            color_name = tense2color(tense)
            changeTense(analyzed_list, tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

    if future_simple == True:
        future_simple = False

        if len(tagged) == 1 and tagged[0][1] in ['VB', 'VBP']:
            tense = 'Future Simple'
            color_name = tense2color(tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        elif len(tagged) > 1:
            if tagged[0][0] == 'be':
                if tagged[1][1] == 'VBG':
                    tense = 'Future Progressive'
                    color_name = tense2color(tense)
                    changeTense(analyzed_list, tense)
                    voice = 'Active'
                    return [button_text[1:], True, color_name, tense, voice]

                elif tagged[1][1] == 'VBN':
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'
                    changeVoice(analyzed_list, voice)
                    return [button_text[1:], True, color_name, tense, voice]

            elif len(tagged) > 2 and tagged[0][0] == 'have':
                if tagged[1][0] == 'been':
                    if tagged[2][1] == 'VBG':
                        tense = 'Future Perfect Progressive'
                        color_name = tense2color(tense)
                        voice = 'Active'
                        changeTense(analyzed_list, tense)
                        return [button_text[1:], True, color_name, tense, voice]

            elif tagged[0][0] in ['VB', 'VBP']:
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice = 'Active'
                return [button_text[1:], True, color_name, tense, voice]

    if future_perfect == True:
        future_perfect = False
        if len(tagged) > 1 and tagged[0][0] == "been":
            tense = 'Future Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Passive'
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]

    if tagged[0][1] == 'VBN':
        if len(tagged) == 1:
            return [tagged[0][0], False, None, None, None]
        else:
            return [tagged[0][0], False, None, None, None], findTense(analyzed_list, tagged[1:])

    # Identify tense
    tense = 'Unidentified'
    color_name = 'grey'
    voice = "Unidentified"
    detail = []
    if len(tagged) == 1:
        if tagged[0][1] == 'VBN':
            return [button_text[1:], False, None, None, None]

        elif tagged[0][1] == 'VBD':
            tense = 'Past Simple'
            voice = 'Active'
            if tagged[0][0] in ["did", "Did", "was", "Was", "were", "Were"]:
                past_simple = True
            if tagged[0][0] in ["had", "Had"]:
                past_perfect = True
            if flag_and == True:
                tense = previous[3]
                voice = previous[4]
            color_name = tense2color(tense)

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            if tagged[0][0] in ['do', "Do", "does", "Does", "is", "Is", "are", "Are", "'s", "'re"]:
                present_simple = True
            if tagged[0][0] in ["has", "Has", "have", "Have"]:
                present_perfect = True

        elif tagged[0][0] in ['can', 'Can']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            present_simple = True

        elif tagged[0][1] == 'VBG':
            return [button_text[1:], False, None, None, None]

        elif tagged[0][0] in ['will', "Will", "'ll"]:
            tense = "Future Simple"
            color_name = tense2color(tense)
            voice = 'Active'
            future_simple = True

    elif len(tagged) == 2:
        if tagged[0][0] in ['was', 'were', 'Was', 'Were']:
            if tagged[1][1] == 'VBN':
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Passive'

            elif tagged[1][1] == 'VBG':
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

        elif tagged[0][0] in ["has", "Has", "have", "Have"] and tagged[1][1] == 'VBN':
            tense = 'Present Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Active'

        elif tagged[0][1] == 'MD' and tagged[0][0] not in ['will', 'Will']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][0] in ["am", "Am","is", "Is", "are", "Are", "'s", "'re", "'m"]:
            if tagged[1][1] == 'VBG':
                tense = 'Present Progressive'
                color_name = tense2color(tense)
                voice = 'Active'

            if tagged[1][1] == 'VBN':
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice = 'Passive'

        elif tagged[0][0] in ['will', 'Will']:
            if tagged[1][1] == 'VB':
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice ='Active'

            if tagged[1][0] == "have":
                tense = 'Future Perfect Simple'
                color_name = tense2color(tense)
                voice = 'Active'
                future_perfect = True

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice = 'Active'

    elif len(tagged) == 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][1] == 'VBD':
                if tagged[0][0] in ["had", "Had"]:
                    tense = 'Past Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Active'

                elif tagged[2][1] in ['VB', 'VBP']:
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

            elif tagged[0][0] in ["could", "Could", "might", "Might"]:
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[0][0] in ["has", "Has", "have", "Have"]:
                tense = 'Present Perfect Simple'
                color_name = tense2color(tense)
                voice = 'Active'

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

        elif tagged[0][0] in ["had", "Had"]:
            if tagged[1][0] == "been":
                if tagged[2][1] == 'VBN':
                    tense = 'Past Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'

                if tagged[2][1] == 'VBG':
                    tense = 'Past Perfect Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[1][1] == 'VBN':
                tense = 'Past Perfect Simple'
                color_name = tense2color(tense)
                voice = 'Active'

        elif tagged[0][0] in ["has", "Has", "have", "Have"]:
            if tagged[1][0] == "been" and tagged[2][1] == 'VBG':
                tense = 'Present Perfect Progressive'
                color_name = tense2color(tense)
                voice = 'Active'

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

            elif tagged[1][0] == "have":
                    tense = 'Future Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Active'

    elif len(tagged) > 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][0] in ['will', 'Will', 'wo', 'Wo']:
                if tagged[2][0] == 'be' and tagged[3][1] == 'VBN':
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

            elif tagged[0][0] in ["has", "Has", "have", "Have"]:
                if tagged[2][0] == 'been' and tagged[3][1] == 'VBG':
                    tense = 'Present Perfect Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

        elif tagged[0][0] in ["will", "Will"]:
            if tagged[1][0] == "have":
                if tagged[2][0] == "been":
                    if tagged[3][1] == 'VBN':
                        tense = 'Future Perfect Simple'
                        color_name = tense2color(tense)
                        voice = 'Active'

                    elif tagged[3][1] == 'VBG':
                        tense = 'Future Perfect Progressive'
                        color_name = tense2color(tense)
                        voice = 'Active'

    return [button_text[1:], True, color_name, tense, voice]

def allFlag2False():
    global past_simple
    past_simple = False

    global past_perfect
    past_perfect = False

    global present_simple
    present_simple = False

    global present_perfect
    present_perfect = False

    global future_simple
    future_simple = False

    global future_perfect
    future_perfect = False

    global flag_and
    flag_and = False

    global flag_get
    flag_get = False

    # global previous_verb
    # previous_verb = None

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
    global flag_and
    global previous

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
                    verb = findTense(analyzed, button_tagged)
                    analyzed.append(verb)
                    previous = verb
                    button_tagged.clear()

                if word_tag[0].isalpha():
                    analyzed_word = [word_tag[0], False, None, None, None]
                    analyzed.append(analyzed_word)
                    if word_tag[0] in ["because"]:
                        allFlag2False()
                    if flag_and == True:
                        flag_and = False
                    if word_tag[0] == 'and':
                        flag_and = True
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
                            ['Past Perfect Progressive', tense2color('Past Perfect Progressive')],
                            ['Present Simple', tense2color('Present Simple')],
                            ['Present Progressive', tense2color('Present Progressive')],
                            ['Present Perfect Simple', tense2color('Present Perfect Simple')],
                            ['Present Perfect Progressive', tense2color('Present Perfect Progressive')],
                            ['Future Simple', tense2color('Future Simple')],
                            ['Future Progressive', tense2color('Future Progressive')],
                            ['Future Perfect Simple', tense2color('Future Perfect Simple')],
                            ['Future Perfect Progressive', tense2color('Future Perfect Progressive')]]

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