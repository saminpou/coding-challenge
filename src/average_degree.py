import re
import datetime
from collections import deque
import sys, getopt

class Node:
	def __init__(self, name=None):
		self.neighbors = {}
		self.date_added = {}
		self.name = name

	
	def addNeighbor(self, name, node):
		if name not in self.neighbors:
			self.neighbors[name] = node

	def removeNeighbors(self, list_datetime, node_set):
		if node_set:
			last_node = self.neighbors[node_set[-1]]
		else:
			return;

		for node_name in node_set:
			node = self.neighbors[node_name]
			# Get the datetime from the node
			last_modified_date = self.date_added[node_name]
			#If the date outside of our window is the date that the node's edge was last modified, remove it
			if last_modified_date == list_datetime:
				#Delete this nodes ref to the other node
				del self.date_added[node_name]
				del self.neighbors[node_name]
				#Delete the other nodes ref to this node
				del node.date_added[self.name]
				del node.neighbors[self.name]
				#Tell the caller that we deleted

		#Remove the node we are about to traverse to
		node_set.pop()

		#Cal removeNeighbors on the next node
		last_node.removeNeighbors(list_datetime, node_set)

	def addNeighbors(self, curr_datetime, nodes):
		if nodes:
			last_node = nodes[-1]
		else:
			return;

		for node in nodes:
			#If the edge already exists, we update the dates added

			if node.name in self.neighbors:
				self.date_added[node.name] = curr_datetime
				node.date_added[self.name] = curr_datetime
			#Otherwise, we add the connection between the two nodes and add the dates
			else:
				self.date_added[node.name] = curr_datetime
				node.date_added[self.name] = curr_datetime

				self.neighbors[node.name] = node
				node.neighbors[self.name] = self

		#Remove the node we are about to traverse to
		nodes.pop()

		#Call removeNeighbors on the next node
		last_node.addNeighbors(curr_datetime, nodes)      
  
	def __getitem__(self, key):
		return self.neighbors[key]

class RollingAverageParser:
	def __init__(self, filename, outfile_name):
		#hashtag -> Node
		self.hashtag_map = {}

		#datestring -> List of Nodes
		self.date_map = {}

		#List of dates
		self.included_dates = []

		#The generated output from the 
		self.tweetfile = open(filename)

		self.outfile_name = outfile_name

	def parse_datetime(self, tweet):
		if tweet:
			r = re.search("timestamp: ", tweet)
			if r:
				end = r.end()
				datetime = tweet[end:-2]
				return datetime

		return None

	def parse_hashtags(self, tweet):
		if tweet:
			hashtags = {tag.strip("#") for tag in tweet.split() if tag.startswith("#")}
			hashtags = set([x.lower() for x in hashtags])
			#print hashtags
			return hashtags

		return None

	def remove_from_window(self, list_datetime):
		if list_datetime in self.date_map:
			# Get the nodes that were added/updated on this date
			node_set = list(self.date_map[list_datetime])

			#Get the first node
			first_node = self.hashtag_map[node_set.pop()]


			#Tell the first node to remove all its matching neighbors
			first_node.removeNeighbors(list_datetime,node_set)

			#If the node has no neighbors, remove them permanently
			node_set_a = list(self.date_map[list_datetime])

			for node_name in node_set_a:
				if len(self.hashtag_map[node_name].neighbors) is 0:
					del self.hashtag_map[node_name]

			#At this point, we have removed all edges added on the specified date, so we can remove the date_map entry
			del self.date_map[list_datetime]

	def get_weight(self):
		weight = 0
		denom = len(self.hashtag_map)
		# print "THe number of nodes is: " + str(denom)
		# print '\n'
		if denom is 0:
			return 0
		else:
			for key,value in self.hashtag_map.iteritems():
				# print "For the key: " + str(key) + " the number of neighbors is: " + str(len(value.neighbors))
				# for k1,node in value.neighbors.iteritems():
				#     print str(k1)
				weight += len(value.neighbors)  

			total_weight = weight / float(denom)
			return round(total_weight,2)


	def read_tweets(self):
		with open(self.outfile_name, 'w') as outfile:
			for tweet in self.tweetfile:
				datetime_str = self.parse_datetime(tweet)

				if not datetime_str:
					continue;

				hashtags = self.parse_hashtags(tweet)
				current_datetime = datetime.datetime.strptime(datetime_str,'%a %b %d %H:%M:%S +0000 %Y') - datetime.timedelta(0,60)
				num_dates_removed = 0
				for date in self.included_dates:
					list_datetime = datetime.datetime.strptime(date,'%a %b %d %H:%M:%S +0000 %Y')

					#if the value is outside of our window
					if current_datetime > list_datetime:
						self.remove_from_window(date)
						num_dates_removed += 1
					else:
						break;

				#Remove the dates that are outside of the window
				if num_dates_removed:
					self.included_dates = self.included_dates[num_dates_removed:]
					num_dates_removed = 0

				#Add or update the tree with the hashtags of the tweets we are currently looking at
				if hashtags and len(hashtags) > 1:
					self.date_map[datetime_str] = hashtags
					self.included_dates.append(datetime_str)			

					current_nodes = []
					#Add the new nodes to a temp list
					for tag in hashtags:
						if tag in self.hashtag_map:  
							current_nodes.append(self.hashtag_map[tag])
						else:
							new_node = Node(tag)
							current_nodes.append(new_node)
							self.hashtag_map[tag] = new_node			

					#Tell the first node to start adding neighbors based on the passed in list
					first_node = current_nodes.pop()
					first_node.addNeighbors(datetime_str, current_nodes)

				#Calculate the weight once the tree has finished being parsed
				weight = self.get_weight()
				outfile.write(str(weight) + '\n')


def main(argv):

	path = argv[1]
	outfile = argv[2]

	rap = RollingAverageParser(path, outfile)
	rap.read_tweets()

if __name__ == "__main__":
   main(sys.argv)

