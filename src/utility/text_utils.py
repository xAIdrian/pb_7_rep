import re

no_space_header_pattern = [
    '#a',
    '#B',
    '#C',
    '#D',
    '#E',
    '#F',
    '#G',
    '#H',
    '#I',
    '#J',
    '#K',
    '#L',
    '#M',
    '#N',
    '#O',
    '#P',
    '#Q',
    '#R',
    '#S',
    '#T',
    '#U',
    '#V',
    '#W',
    '#X',
    '#Y',
    '#Z',
]

def groom_title(input_string):
    # Define the regular expression pattern
    pattern = r"#\s?H1[-:]?\s?|#\s?|\s?<h1>\s?|</h1>|\s?<H1>\s?|</H1>"
    # this pattern removes all whitespaces pattern = r"#\s?H1[-:]?\s?|#\s?|\s?<h1>\s?|</h1>|\s?"
    title = re.sub(pattern, "", input_string)

    print(f'formatted title: {title}')
    return title


def groom_body(input_string):
    for check in no_space_header_pattern:
        split = list(check)
        solution = f'{split[0]} {split[1]}'
        input_string = input_string.replace(check, solution)

    input_string = input_string.replace("<h2>", "<p></p><h2>")  
    
    return input_string    