import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import nltk

class CheckTense:
	def __init__(self, window):
		# window title and size
		self.master = window
		self.master.title("Narative tenses")
		self.master.minsize(500,500)

		# Input form
		## Label
		self.label = ttk.Label(self.master, text = " Enter the story")
		self.label.config(font=("Times New Roman", 15))
		self.label.pack()
		## Input text box
		self.textFrame = ScrolledText(self.master, width=100, height=10, relief="solid")
		self.textFrame.config(font=("Times New Roman", 12))
		self.textFrame.pack()
		## Run buttun
		self.checkTense_btn = tk.Button(self.master, text='Start Analyzing', command=self.onClick)
		self.checkTense_btn.config(font=("Times New Roman", 12))
		self.checkTense_btn.pack()

		# Result text box
		self.result_box = ScrolledText(self.master, width=100, height=10, background="light grey")
		self.result_box.config(state=tk.DISABLED, wrap=tk.WORD, font=("Times New Roman", 12))
		self.result_box.pack()

		# Detailed text box
		self.detailed_box = ScrolledText(self.master, width=100, height=10, background="light grey")
		self.detailed_box.config(state=tk.DISABLED, wrap=tk.WORD, font=("Times New Roman", 12))
		self.detailed_box.pack()

	# Function on clicking start
	def onClick(self):	
		text = self.textFrame.get('1.0', tk.END)  # Get all text in widget.
		paragraphs = text.split("\n") # Split into paragraphs

		# Analyze each paragraph
		self.result_box.config(state=tk.NORMAL)
		self.result_box.delete('1.0', tk.END)
		for p in paragraphs:
			token = nltk.word_tokenize(p)
			tagged = nltk.pos_tag(token)
			self.insertResult(tagged)

		self.result_box.config(state=tk.DISABLED)
		
	# Insert result to the result text box
	# Different tenses have different colors
	def insertResult(self, tagged):
		button_tagged = []
		for word_tag in tagged:
			if word_tag[1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD'] or word_tag[0] in ['not', 'Not']:
				button_tagged.append(word_tag)
			else:
				if button_tagged:
					self.result_box.insert('end-1c', ' ')
					button_text, tense, color_name, detail = self.findTense(button_tagged)
					self.result_box.window_create(self.result_box.index('end'), window = tk.Button(self.result_box, text=button_text, 
						background=color_name, command=lambda x=button_text, y=tense, z=detail: self.tense_onClick(x, y, z)))
					button_tagged.clear()

				if word_tag[0].isalpha(): 
					self.result_box.insert('end-1c', ' ')

				self.result_box.insert('end-1c', word_tag[0])
				in_group = False

		self.result_box.insert('end-1c', '\n')

	# Matching tense with color
	def tense2color(self, tense):
		if tense == 'Past Simple':
			return 'cornflower blue'

		if tense == 'Past Progressive':
			return 'medium slate blue'

		if tense == 'Past Perfect Simple':
			return 'royal blue'

		if tense == 'Present Simple':
			return 'turquoise'

		if tense == 'Present Progressive':
			return 'cyan'

		if tense == 'Future Simple':
			return 'pale green'

		return 'grey'
	# Convert tagged word list into string
	# Identify tense and return the color correspoding to the tense
	def findTense(self, tagged):
		# Convert tagged word list into string
		button_text = ''
		for word_tag in tagged:
			button_text += ' ' + word_tag[0]

		# Identify tense
		tense = 'Unidentified'
		color_name = 'grey'
		detail = []
		if len(tagged) == 1:
			if tagged[0][1] == 'VBD':
				tense = 'Past Simple'
				color_name = self.tense2color(tense)
				detail.append('Active')

			elif tagged[0][1] in ['VB', 'VBP', 'VBZ']:
				tense = 'Present Simple'
				color_name = self.tense2color(tense)
				detail.append('Active')

			elif tagged[0][1] == 'VBG':
				tense = 'Present Progressive'
				color_name = self.tense2color(tense)
				detail.append('Active')

		elif len(tagged) == 2:
			if tagged[0][0] in ['was', 'were', 'Was', 'Were'] and tagged[1][1] == 'VBN':
				tense = 'Past Simple'
				color_name = self.tense2color(tense)
				detail.append('Passive')

			if tagged[0][0] in ['was', 'were', 'Was', 'Were'] and tagged[1][1] == 'VBG':
				tense = 'Past Progressive'
				color_name = self.tense2color(tense)
				detail.append('Active')

			elif tagged[0][0] == 'had' and tagged[1][1] == 'VBN':
				tense = 'Past Perfect Simple'
				color_name = self.tense2color(tense)
				detail.append('Active')

			elif tagged[0][1] == 'MD' and tagged[0][0] not in ['will', 'Will']:
				tense = 'Present Simple'
				color_name = self.tense2color(tense)
				detail.append('Active')

			elif tagged[0][0] in ['will', 'Will'] and tagged[1][1] == 'VB':
				tense = 'Future Simple'
				color_name = self.tense2color(tense)
				detail.append('Active')

		elif len(tagged) == 3:
			if tagged[0][0] not in ['have', 'has', 'had', 'Have', 'Has', 'Had']:
				if tagged[0][1] == 'VBD':
					tense = 'Past Simple'
					color_name = self.tense2color(tense)
					detail.append('Active')

		return button_text[1:], tense, color_name, detail

	# Event on clicking analyzed verb
	# Insert detailed information in detailed textbox
	def tense_onClick(self, word, tense, detail):
		self.detailed_box.config(state=tk.NORMAL)
		self.detailed_box.delete('1.0', tk.END)
		self.detailed_box.insert('end-1c', 'Verb: ' + word + '\n')
		self.detailed_box.insert('end-1c', 'Tense: ' + tense + '\n')
		if detail:
			self.detailed_box.insert('end-1c', 'Voice: ' + detail[0] + '\n')
		self.detailed_box.config(state=tk.DISABLED)
		

# Main function
window = tk.Tk()
main_window = CheckTense(window)
window.mainloop()