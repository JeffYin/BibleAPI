'''
API server: https://api.biblesupersearch.com/api
Bible Version: Chinese Union Simplified"
'''
import json
import re
import requests

class BibleVerse:
    def __init__(self, bookName, chapter, verses):
        self.bookName = bookName
        self.chapter = chapter
        self.verses = verses
        self._englishAbbr = None
        self._text = None

    @property
    def englishAbbr(self):
        return self._englishAbbr

    @englishAbbr.setter
    def englishAbbr(self, value):
        self._englishAbbr = value

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        
    def __str__(self):
        return f"{self.bookName} {self.chapter}:{self.verses} {self.text}"

def read_bible_books():
    with open("bible_books.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        books = data["books"]
        bible_books_dict = {}
        for book in books:
            chinese_abbr = book["Chinese_abbreviation"]
            english_abbr = book["English_abbreviation"]
            # Put the above fields into the dictionary
            bible_books_dict[chinese_abbr] = english_abbr
    # Return the dictionary
    return bible_books_dict


def convert_string_to_bible_verses(input_string):
    split_string = re.split(r"[,;，]", input_string)
    bible_verses = []
    book_name, chapter, verses = '',1,1
    for item in split_string:
        pattern = re.compile(r"([\u4e00-\u9fa5]{1,2})(\d{1,2}):(.*)")
        match = pattern.match(item)
        if match:
            book_name = match.group(1)
            chapter = match.group(2)
            verses = match.group(3)
        else:
            pattern = re.compile(r"(\d{1,2}):(.*)")
            match = pattern.match(item)
            if match:
                chapter = match.group(1)
                verses = match.group(2)
            else:
                verses = item
        # Create a BibleVerse object with the extracted book_name, chapter, and verses
        bible_verse = BibleVerse(book_name, chapter, verses)
        # Append bible_verse to the verses list
        bible_verses.append(bible_verse)

    return bible_verses

def get_all_versers():
    all_verses = []
    with open("questions.txt", "r", encoding="utf-8") as file:
        # Read all lines of the file
        lines = file.readlines()
        # Loop through each line in the lines list
        for line in lines:
        # Replace the characters as specified
            line = line.replace("（", "(").replace("）", ")").replace("：", ":").replace("，",",").replace("；",",").replace("、",",")
            start = line.find("(") + 1
            end = line.find(")")
            # Output start and end in the format "start: end"
            if start>0: 
                extracted_text = line[start:end]
                # Remove all blanks from the extracted_text
                extracted_text = extracted_text.replace(" ", "")
                
                bible_verses = convert_string_to_bible_verses(extracted_text)
                # Add each item of bible_verses into all_verses
                for verse in bible_verses:
                    all_verses.append(verse)
    return all_verses                

def convert_to_English_bible_verses(bible_verses_list):
    bible_boooks = read_bible_books()
    english_verses = []
    for verse in bible_verses_list:
        # Get the value from the dictionary bible_books bo        
        english_book_name = bible_boooks.get(verse.bookName)
        verse.englishAbbr = english_book_name


def call_api(english_verses):
    base_url = "https://api.biblesupersearch.com/api?bible=chinese_union_simp"
    #base_url = "http://ibibles.net/quote.php?CUS"
    api_results = []

    for verse in english_verses:
        verse_info = f"{verse.englishAbbr} {verse.chapter}:{verse.verses}"
    
        # Construct the API request URL
        #request_url = f"{base_url}-{verse_info}"
        request_url = f"{base_url}&reference={verse_info}"
        
        # Send the API request and get the response
        response = requests.get(request_url)
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Parse the JSON response
            json_data = response.json()
                        
            for result in json_data["results"]:
                verses = result["verses"]
                chinese_union_simp = verses["chinese_union_simp"]
                for chapter, chapter_detail in chinese_union_simp.items():
                    for verse_number, verse_detail in chapter_detail.items():
                        text = verse_detail['text'].replace(" ", "")
                        info = f"{verse.bookName} {chapter}:{verse_number} {text}"
                        print(info)
                    
        else:
            print(f"Error: Unable to fetch data for {verse}")
  
        #break  # Break the for loop

    return api_results


all_verses = get_all_versers()
convert_to_English_bible_verses(all_verses)
call_api(all_verses)

    
                
        
    