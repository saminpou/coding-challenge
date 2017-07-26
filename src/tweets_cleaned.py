import urllib, json, string, re
import sys
from collections import OrderedDict
import csv
import operator
import datetime, time
import unicodedata

class TweetParser:
	def __init__(self,filename, outfile_name):
		self.unicode_counter = 0
		self.tweets = []
		self.txtfile  = open(filename)
		self.output = {}
		self.outfile_name = outfile_name
		for line in self.txtfile:
			self.tweets.append(json.loads(line))

	def contains_unicode(self,text):
		if isinstance(text, unicode):
			return True
		else:
			return False

	def clear_unicode(self,text):
		#import pdb;pdb.set_trace();
		return unicodedata.normalize('NFKD', text).encode('ascii','ignore')

	def generate_output(self):
		with open(self.outfile_name, 'w') as outfile:

			for tweet in self.tweets:
				#check if the json obj is a tweet
				if "created_at" in tweet:
					created_at = tweet["created_at"]
					text = tweet["text"]

					#Increment unicode_counter and clear unicode
					if self.contains_unicode(text):
						self.unicode_counter +=1
						text = self.clear_unicode(text)
						text = text.replace('\r', ' ').replace('\n', ' ')
						#print text
					
					entry = str(text) + " (timestamp: " + str(created_at) + ")\n" 
					outfile.write(entry)

			#We wrote all the tweets needed to be written
			#Output that last line
			outfile.write(str(self.unicode_counter) + " tweets contained unicode.")

def main(argv):
	path = argv[1]
	outfile = argv[2]
	parser = TweetParser(path, outfile)
	parser.generate_output()

if __name__ == "__main__":
   main(sys.argv)
