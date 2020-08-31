from flask import Flask, render_template, flash, request, Markup
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import nltk

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
        return '#4097FF'

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

    if flag_and == True: #... and ...
        if tagged[0][1] == 'VBG' and previous[3] in ['Past Progressive', 'Preset Progressive', 'Future Progressive']: # ... and Ving
            tense = previous[3]
            color_name = tense2color(tense)
            voice = previous[4]
            return [button_text[1:], True, color_name, tense, voice]
        if tagged[0][1] in ['VBN'] and (previous[3] in ['Past Perfect Simple', 'Present Perfect Simple', 'Future Perfect Simple'] or previous[4] == 'Passive'): # ...and V(past participle)
            tense = previous[3]
            color_name = tense2color(tense)
            voice = previous[4]
            return [button_text[1:], True, color_name, tense, voice]

    if flag_get == True: 
        if tagged[0][1] == 'VBN': # ... get ... V(past participle)
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
        if tagged[0][1] in ['VB', 'VBP']: # ... did ... V(base)
            tense = 'Past Simple'
            color_name = tense2color(tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        if tagged[0][1] == 'VBG': # ... was/were ... V(ing)
            tense = 'Past Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]
            
        if tagged[0][1] == 'VBN': # ... was/were ... V(past participle)
            tense = 'Past Simple'
            color_name = tense2color(tense)
            voice = "Passive"
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]

    if past_perfect == True:
        past_perfect = False
        if tagged[0][1] == 'VBN': # ... had ... V(past partciple)
            tense = 'Past Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]

    if present_simple == True:
        present_simple = False
        if tagged[0][1] == 'VBG':  # ... am/is/are ... V(ing)
            tense = 'Present Progressive'
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]

        if tagged[0][1] == 'VBN': # ... am/is/are ... V(past participle)
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice = "Passive"
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]

    if present_perfect == True:
        present_perfect = False

        if len(tagged) == 1 and tagged[0][1] == 'VBN': # ... has/have ... V(past participle)
            tense = 'Present Perfect Simple'
            color_name = tense2color(tense)
            changeTense(analyzed_list, tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        if len(tagged) > 1 and tagged[0][0] == "been" and tagged[1][1] == 'VBG': # ... has/have ... been V(ing)
            tense = 'Present Perfect Progressive'
            color_name = tense2color(tense)
            changeTense(analyzed_list, tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        if len(tagged) > 1 and tagged[0][0] == "been" and tagged[1][1] == 'VBN': # ... has/have ... been V(past participle)
            tense = 'Present Perfect Simple'
            color_name = tense2color(tense)
            changeTense(analyzed_list, tense)
            voice = 'Passive'
            return [button_text[1:], True, color_name, tense, voice]

    if future_simple == True:
        future_simple = False

        if len(tagged) == 1 and tagged[0][1] in ['VB', 'VBP']: # ... will ... V(bare)
            tense = 'Future Simple'
            color_name = tense2color(tense)
            voice = 'Active'
            return [button_text[1:], True, color_name, tense, voice]

        elif len(tagged) > 1:
            if tagged[0][0] == 'be':
                if tagged[1][1] == 'VBG': # ... will ... be V(ing)
                    tense = 'Future Progressive'
                    color_name = tense2color(tense)
                    changeTense(analyzed_list, tense)
                    voice = 'Active'
                    return [button_text[1:], True, color_name, tense, voice]

                elif tagged[1][1] == 'VBN': # ... will ... be V(past participle)
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'
                    changeVoice(analyzed_list, voice)
                    return [button_text[1:], True, color_name, tense, voice]

            elif len(tagged) > 2 and tagged[0][0] == 'have': 
                if tagged[1][0] == 'been':
                    if tagged[2][1] == 'VBG': # ... will ... have been V(past participle)
                        tense = 'Future Perfect Progressive'
                        color_name = tense2color(tense)
                        voice = 'Active'
                        changeTense(analyzed_list, tense)
                        return [button_text[1:], True, color_name, tense, voice]

            elif tagged[0][0] in ['VB', 'VBP']: # ... will ... be V(bare) V(any form)...
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice = 'Active'
                return [button_text[1:], True, color_name, tense, voice]

    if future_perfect == True:
        future_perfect = False
        if len(tagged) > 1 and tagged[0][0] == "been": # ... will have ... been V(past participle)
            tense = 'Future Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Passive'
            changeTense(analyzed_list, tense)
            changeVoice(analyzed_list, voice)
            return [button_text[1:], True, color_name, tense, voice]

        if tagged[0][1] == 'VBN':
            tense = 'Future Perfect Simple' # ... will have ... V(past participle)
            color_name = tense2color(tense)
            voice = 'Active'
            changeTense(analyzed_list, tense)
            return [button_text[1:], True, color_name, tense, voice]

    if tagged[0][1] == 'VBN': # ... V(past participle)
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
        if tagged[0][1] == 'VBN': # ... V(past participle)
            return [button_text[1:], False, None, None, None]

        elif tagged[0][1] == 'VBD': # ... V(past)
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

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']: # ... V(present)
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            if tagged[0][0] in ['do', "Do", "does", "Does", "is", "Is", "are", "Are", "'s", "'re"]:
                present_simple = True
            if tagged[0][0] in ["has", "Has", "have", "Have"]:
                present_perfect = True

        elif tagged[0][0] in ['can', 'Can']: # ... can
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'
            present_simple = True

        elif tagged[0][1] == 'VBG': # ... V(ing)
            return [button_text[1:], False, None, None, None]

        elif tagged[0][0] in ['will', "Will", "'ll"]: # ... will
            tense = "Future Simple"
            color_name = tense2color(tense)
            voice = 'Active'
            future_simple = True

    elif len(tagged) == 2:
        if tagged[0][0] in ['was', 'were', 'Was', 'Were']:
            if tagged[1][1] == 'VBN': # ... was/were V(past participle)
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Passive'

            elif tagged[1][1] == 'VBG': # ... was/were V(ing)
                tense = 'Past Progressive'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[1][0] in ["not", "n't"]: #... was/were not
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'
                past_simple = True

        elif tagged[0][0] == 'had' and tagged[1][1] == 'VBN': # ... had V(past participle)
            tense = 'Past Perfect Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[1][0] in ["not", "n't"]:
            if tagged[0][1] in ['VB', 'VBP', 'VBZ']: # ... do/does/an/is/are not
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice ='Active'
            elif tagged[0][1] in ['VBD', 'VBN']: # ... did/was/were not
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

        elif tagged[0][0] in ["has", "Has", "have", "Have"] and tagged[1][1] == 'VBN': # ... has/have V(past participle)
            tense = 'Present Perfect Simple'
            color_name = tense2color(tense)
            voice = 'Active'

        elif tagged[0][1] == 'MD' and tagged[0][0] not in ['will', 'Will']: # ... can/should/must V(bare) 
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice ='Active'

        elif tagged[0][0] in ["am", "Am","is", "Is", "are", "Are", "'s", "'re", "'m"]:
            if tagged[1][1] == 'VBG': # ... am/is/are V(ing)
                tense = 'Present Progressive'
                color_name = tense2color(tense)
                voice = 'Active'

            if tagged[1][1] == 'VBN': # ... am/is/are V(past participle)
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice = 'Passive'

        elif tagged[0][0] in ['will', 'Will']:
            if tagged[1][1] == 'VB': # ... will V(bare)
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice ='Active'

            if tagged[1][0] == "have": # ... will have
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice = 'Active'
                future_perfect = True

        elif tagged[0][1] in ['VB', 'VBP', 'VBZ']: # ... V(present) V(any form)
            tense = 'Present Simple'
            color_name = tense2color(tense)
            voice = 'Active'

    elif len(tagged) == 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][1] == 'VBD':
                if tagged[0][0] in ["had", "Had"]: # ... had not V(past participle)
                    tense = 'Past Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Active'

                elif tagged[2][1] in ['VB', 'VBP']: # ... dis/was/were not V(bare)
                    tense = 'Past Simple'
                    color_name = tense2color(tense)
                    voice ='Active' 

                elif tagged[2][1] in ['VBD', 'VBN']: # ... was/were not V(past participle)
                    tense = 'Past Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

                elif tagged[2][1] == 'VBG': # ... was/were not V(ing)
                    tense = 'Past Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[0][0] in ["could", "Could", "might", "Might"]: # ... could/might not V(bare)
                tense = 'Past Simple'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[0][0] in ["has", "Has", "have", "Have"]: # ... has/have not V(past participle)
                tense = 'Present Perfect Simple'
                color_name = tense2color(tense)
                voice = 'Active'

            elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
                if tagged[2][1] in ['VB', 'VBP']: # ... do/does not V(present)
                    tense = 'Present Simple'
                    color_name = tense2color(tense)
                    voice ='Active'

                elif tagged[2][1] in ['VBD', 'VBN']: # ... am/is/are not V(past participle)
                    tense = 'Present Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

                elif tagged[2][1] == 'VBG': # ... am/is.are not V(ing)
                    tense = 'Present Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[0][0] in ['ca', 'Ca']: # ... can't V(bare)
                tense = 'Present Simple'
                color_name = tense2color(tense)
                voice ='Active'

            elif tagged[0][0] in ['will', 'Will', 'wo', 'Wo']: # ... will not V(bare)
                tense = 'Future Simple'
                color_name = tense2color(tense)
                voice ='Active'

        elif tagged[0][0] in ["had", "Had"]:
            if tagged[1][0] == "been":
                if tagged[2][1] == 'VBN': # ... had been V(past participle)
                    tense = 'Past Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'

                if tagged[2][1] == 'VBG': # ... had been V(ing)
                    tense = 'Past Perfect Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

            elif tagged[1][1] == 'VBN': # ... had V(past participle) V(any form)
                tense = 'Past Perfect Simple'
                color_name = tense2color(tense)
                voice = 'Active'

        elif tagged[0][0] in ["has", "Has", "have", "Have"]:
            if tagged[1][0] == "been":
                if tagged[2][1] == 'VBG': # ... has/have been V(ing)
                    tense = 'Present Perfect Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

                elif tagged[2][1] == 'VBN': # ... has/have been V(past participle)
                    tense = 'Present Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'

        elif tagged[0][0] in ["will", "Will"]:
            if tagged[1][0] == "be":
                if tagged[2][1] == 'VBG': # ... will be V(ing)
                    tense = 'Future Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

                elif tagged[2][1] == 'VBN': # ... will be V(past participle)
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice = 'Passive'

            elif tagged[1][0] == "have": # ... will have V(past participle)
                    tense = 'Future Perfect Simple'
                    color_name = tense2color(tense)
                    voice = 'Active'

    elif len(tagged) > 3:
        if tagged[1][0] in ["not", "n't"]:
            if tagged[0][0] in ['will', 'Will', 'wo', 'Wo']:
                if tagged[2][0] == 'be' and tagged[3][1] == 'VBN': # ... will not be V(past participle)
                    tense = 'Future Simple'
                    color_name = tense2color(tense)
                    voice ='Passive'

            elif tagged[0][0] in ["has", "Has", "have", "Have"]:
                if tagged[2][0] == 'been' and tagged[3][1] == 'VBG': # ... has/have not been Ving(past participle)
                    tense = 'Present Perfect Progressive'
                    color_name = tense2color(tense)
                    voice = 'Active'

        elif tagged[0][0] in ["will", "Will"]:
            if tagged[1][0] == "have":
                if tagged[2][0] == "been":
                    if tagged[3][1] == 'VBN': # ... will have been V(past participle)
                        tense = 'Future Perfect Simple'
                        color_name = tense2color(tense)
                        voice = 'Active'

                    elif tagged[3][1] == 'VBG': # ... will have been V(ing) 
                        tense = 'Future Perfect Progressive'
                        color_name = tense2color(tense)
                        voice = 'Active'

    return [button_text[1:], True, color_name, tense, voice]

# Set all flag to fail
# Use whenever reach the end of a clause
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


# Change the tense of the closest verb in the list
# Match the color for the new tense
def changeTense(analyzed_list,tense):
    for i in reversed(analyzed_list):
        if i[1]:
            i[3] = tense
            i[2] = tense2color(tense)
            break

# Change the voice of the closest verb in the list
def changeVoice(analyzed_list, voice):
    for i in reversed(analyzed_list):
        if i[1]:
            i[4] = voice
        break

# Analyze the story
# Return a list of words and verb phases with detail
# E.g. [[word1, detail1], [word2, detail2], [word3, detail3], ...]
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
            word_tag = list(word_tag)
            if word_tag[1] == 'NNP' : # When "Are" and "Did" appear first in a sentence, nltk tagger mark them as 'NNP'
                if word_tag[0] in ["are", "Are"]:
                    word_tag[1] = 'VBP'
                elif word_tag[0] in ["did", "Did"]:
                    word_tag[1] = 'VBD'

            if word_tag[1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD'] or word_tag[0] in ["not", "Not", "n't"]: # Add word to verb phrase
                button_tagged.append(word_tag)
            else:
                # Add verb phrase to list
                if button_tagged:
                    verb = findTense(analyzed, button_tagged)
                    analyzed.append(verb)
                    previous = verb
                    button_tagged.clear()

                # Add word to list
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

        # Add break line at the end of paragraph
        analyzed_break_line = (Markup('<br>'), None, None, None, None)
        analyzed.append(analyzed_break_line)

    return analyzed


class Form(Form):
    @app.route("/", methods=['GET', 'POST'])
    def main():
        # Analyze story
        analyzed = None
        story = request.args.get('story')
        if story is not None:
            analyzed = analyze_text(story)

        # Annotation for tenses
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

        # When a verb phrase is clicked
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