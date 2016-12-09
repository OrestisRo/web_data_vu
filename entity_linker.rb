require 'ruby-spark'
require 'warc'
require 'nokogiri'
require 'rake_text'


def initialize_spark
	Spark.start
	yield Spark.context
end

def stop_spark
	Spark.stop
end

def extract_text text_list
	initialize_spark do |sc|
		text_rdd = sc.parallelize(text_list).map(lambda{|t| t.gsub(/\s+/, " ")})
		text_rdd.collect
	end
end


file_path = ARGV[0]

records = Warc.open_stream(file_path)

contents = records.map do |r|
	r.content if r.header["WARC-Type"] == "response"	
end

parsed_content = contents.map {|c| Nokogiri::HTML.fragment c}

text_list = parsed_content.map {|pc| pc.css('p').text}

refined_text = text_list.join(" ").gsub(/\s+/, " ")

rake = RakeText.new

keywords = rake.analyse refined_text, RakeText.SMART, true
puts keywords	





			
		


