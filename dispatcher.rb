require treat
include Treat::Core::DSL
# 1. Sentence Detector
# 2. Tokenizer
# 3. To think if I need to fill in here.
# 4. Name Finder
# 5. POS Tagger
# 6. Chunker
# 7. Parser


string_input = paragraph("Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/;[1][2] born August 4, 1961) is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States House of Representatives in 2000 against incumbent Bobby Rush.")
sentence_array =  string_input.segment


$i=0
until $i>=sentence_array.length-1 do
	$j=0
	token_array = sentence_array[i].tokenize
	until $i>=token_array.length-1 do
		token_array[i].tag
		token_array[i].stem
	end
end

#According to the manual, this syntax will do all the preprocessing necessary to up to the POS tagger. I'm not sure if this will include the NER. If not, it can be achieved by using opennlp tools by the same git project.
#Using the opennlp binder:
#NameFinderME nameFinder = new NameFinderME(model);
#By including all the models and possibly the jars provided in the installation guide, we will be able to extract the named entities we need, to begin with.
string_input.apply(:chunk, :segment, :tokenize, :name_tag)
