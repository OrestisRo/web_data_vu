# README #
### Dependencies ###
## Active libraries ##
* nltk - sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
* sys
* bs4 - BeautifulSoup
* requests
* gzip
* json
* os
* requests

## Possibly included in the future ##
* Levenstein: https://pypi.python.org/pypi/python-Levenshtein/0.12.0

### Code execution ###
There are two implementations currently active at the moment. One that is working without using spark, and one that attempts to use it, but it is not working.
# Comments on the code #
Due to some missunderstanding the first argument described in the assignment is not currently active. That means that we expect 3 arguments, but we don't take into account the first one. We expect (1)"Warc-key"(which is going to be ignored) (2)"input.warc.gz" (3)"output_file"
Currently what the code does, is that:
1 - It takes the warc.gz file, and from that it extracts all individual warc-type: response, along with the warc-record-id and respective html raw response.
2 - For each html page given, extracts all raw text.
3 - Tokenizes the text into sentences.
4 - Tokenizes the sentences into words.
5 - POS-Tagging the word-tokens.
6 - Runs chunking and named entity recognition on the POS-Tagged tokens.
7 - Parsing the entities and keeping the unique ones.
8 - For each unique entity, query the freebase.
9 - Get response results and save the highest score number.
10 - Locate the first item in response that matches the saved score.
11 - Extract label and freebase id and convert them to the representation that suits us.
12 - Collect all of the data and write in the output_file in the format of warc-record-id {tab} entity_label {tab} entity_frebase_id

# WDPS_group6_nospark.py #
* Syntax: python WDPS_group6_nospark.py "warc-record-id" "sample.warc.gz" "sample_output.tsv"

# WDPS_group6_parser_spark.py #
* Same syntax, not working file.