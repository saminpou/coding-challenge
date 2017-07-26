#!/usr/bin/env bash

echo " tweets_cleaned.py"
python ./src/tweets_cleaned.py ./tweet_input/tweets.txt ./tweet_output/ft1.txt


echo " average_degree.py" 
python ./src/average_degree.py ./tweet_output/ft1.txt ./tweet_output/ft2.txt

