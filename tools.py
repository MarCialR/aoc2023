from os import path
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from types import SimpleNamespace

from httplib2 import Http

from IPython.display import display_markdown
YEAR = "2023"
AOC_URL = f"https://adventofcode.com/{YEAR}/day/%d"
PUZZLE_HTML_FILE = "./descriptions/html%d.txt"
PUZZLE_DATA_FILE = "./data/puzzle%d.txt"
PUZZLE_TEST_DATA_FILE = "./data/test%d.txt"

dbg_forcereload = False

   
def get_puzzle(day, debug=False):
    
    # problem_1 - markdown printable on the Ipython notebook cell
    # data - (Puzzle inputs differ by user) 
    #        place your puzzle input in a file named data/puzzle<day>.txt 
    
    problem_1 = get_problem_1(day)
    data = get_data(day)
    test = get_test_data(day)
    
    return SimpleNamespace (**{'day': day, 'problem_1':problem_1, "data" : data, "test" : test} )

def get_html(day):
    if path.exists(PUZZLE_HTML_FILE % day):
        with open (PUZZLE_HTML_FILE % day) as f:
            return f.read()
    print("downloading html.../n")
    http = Http()
    content = http.request(AOC_URL % day)
    html_content = content[1].decode()
    with open(PUZZLE_HTML_FILE % day, "w") as f:
        f.write(html_content)
    return html_content

def parse_article (article_html):
    # generate markdown 
    parser = AoCParser()
    parser.feed(article_html)
    return parser.out

def get_problem_1(day):
    html_content = get_html(day)
    #print (html_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    return parse_article (soup.find_all('article')[0].prettify( formatter="html" ))
    
        
def get_problem_2(puzzle):
    if not path.exists(PUZZLE_HTML_FILE % puzzle.day):
        print("problem 2 cannot be loaded until problem 1 is solved and the new html is copied onto " + PUZZLE_HTML_FILE % puzzle.day)
    
    with open (PUZZLE_HTML_FILE % puzzle.day) as f:
        html_content= f.read()    
    # generate markdown 
    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        markdown = parse_article (soup.find_all('article')[1].prettify( formatter="html" ))
        return markdown
    except IndexError:
        print("problem 2 cannot be loaded until problem 1 is solved and the new html is copied onto " + PUZZLE_HTML_FILE % puzzle.day)
        

def get_data(day):
    puzzle_file = PUZZLE_DATA_FILE % day
    if path.exists(puzzle_file):
        with open (puzzle_file) as f:
            return f.read().splitlines()
    else:
        text = """Note: Puzzle inputs differ by user
Place your puzzle data in a file %s in the data folder""" % puzzle_file
        print(text)
        return text

def get_test_data(day):
    puzzle_file = PUZZLE_TEST_DATA_FILE % day
    if path.exists(puzzle_file):
        with open (puzzle_file) as f:
            return f.read().splitlines()
    else:
        text = """Note: Puzzle inputs differ by user
Place your puzzle data in a file %s in the data folder""" % puzzle_file
        print(text)
        return text

    
def show_problem_1(puzzle, debug=False) :
    display_markdown(AOC_URL % puzzle.day + "\n" + puzzle.problem_1, raw=True)


def show_problem_2(puzzle, debug=False):
    markdown = get_problem_2(puzzle)
    display_markdown(markdown, raw=True)


class AoCParser(HTMLParser):
    # converts HTML to Markdown according to:
    # https://www.markdownguide.org/basic-syntax/#code

    def __init__(self, debug=False):
        super(AoCParser, self).__init__()
        self.stack = []
        self.out = ""
        self.buffer = ""
        self.codebuffer = ""
        self.dbg = debug
        self.link = ""
        self.multilinecode = False
    
    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if self.dbg:
            print("Encountered a start tag:", tag)
            print (self.stack)
            print(attrs)
        if tag == "li":
            self.buffer += "+ "
        elif tag == "h2":
            self.buffer += "## "
        elif tag == "code":
            self.codebuffer += "`"
        elif tag == "em":
            if "code" not in self.stack:
                    self.buffer += " **"                   
       
        elif tag == "a":
            self.link = dict(attrs)["href"]
            self.buffer += " [" 

    def handle_endtag(self, tag):
        assert tag == self.stack.pop()
        
        if tag == "h2" or tag == "p" or tag == "pre" :
            self.buffer += "\n\n"
            
        elif tag == "li":
            self.buffer += "\n"
            
        elif tag == "ul":
            self.buffer += "\n"

        elif tag == "code":
            if self.multilinecode:
                # horrible code to fix some issue when the first chars of a code block are numbers
                # not sure about the reason though. this just fixes it
                self.codebuffer="```\n " + "\n ".join(self.codebuffer[1:].splitlines()) + "\n\n```"
                self.multilinecode = False
            else:
                self.codebuffer += "`"    
            self.buffer += self.codebuffer
            self.codebuffer =""

        elif tag == "em":
            if "code" not in self.stack:
                self.buffer += "** "    
            
        elif tag == "a":
            self.buffer += "](" + self.link + ") "
            self.link = ""
            
        if len(self.stack)==1:
            self.out += self.buffer + "\n"
            self.buffer = ""
            
        if self.dbg:
            print("Encountered an end tag :", tag)
            print("Stack :", self.stack)

    def handle_data(self, data):
        if len(self.stack) == 0:
            # we are at root of article
            return

        if self.stack[-1] == "code" and data.find("\n"):
            self.multilinecode =True
            self.codebuffer += data
        else:
            self.buffer += data.strip()

        
        if self.dbg:
            print("last tag: " + self.stack[-1] + "  Encountered some data  :", data)

