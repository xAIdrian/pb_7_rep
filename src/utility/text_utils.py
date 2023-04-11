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
    title = title.replace('"', '')

    # Remove any invalid characters from the title
    title = re.sub(r'[^\w\s-]', '', title).strip()
    # Make sure the title is no longer than 100 characters
    title = title[:100]

    print(f'formatted title: {title}')
    return title


def groom_body(input_string):
    for check in no_space_header_pattern:
        split = list(check)
        solution = f'{split[0]} {split[1]}'
        input_string = input_string.replace(check, solution)

    input_string = input_string.replace("<h2>", "<p></p><h2>")  
    
    return input_string    

def format_yt_description(description):
    # Limit description to 5000 characters
    if len(description) > 5000:
        description = description[:5000]

    # Replace common special characters with their HTML entities
    description = description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

    # Remove unsupported HTML tags
    description = re.sub(r'<[^>]*>', '', description)

    return description
  
def format_yt_title(title):
    # Limit title to 100 characters
    if len(title) > 100:
        title = title[:100]

    # Replace common special characters with their HTML entities
    title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "").replace("'", "")

    # Remove unsupported HTML tags
    title = re.sub(r'<[^>]*>', '', title)

    return title  