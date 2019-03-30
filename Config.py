# You should probably set these two as environment variables instead
SPREADSHEET_ID = ''
DEST_ID = ''

# Excel formula thing representing the cell range to look at.
# {0} will be replaced with the total row count.
SPREADSHEET_RANGE_FORMAT = 'B8:D{0}'

# If changing scopes, DELETE the file "token.pickle"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.file']

PRIMARY_COLOR = (0, 0, 0, 255)
SECONDARY_COLOR = (255, 255, 255, 255)

# Program won't necessarily obey box's position; will try to center vertically and text will naturally be
# cut off a little before the max width. However, it will change font size to accomodate the box height.
BOX = (50, 50, 400, 400) # (x, y) of top-left corner, followed by width and height of box - in absolute px
DIM = (500, 500) # image width, height - px

FONT_PATH = 'Garamond.ttf' # use a TrueType font
FONT_SIZE = 18 # for especially long blocks of text, fontsize will be reduced.
GAP_HEIGHT = 25 # pixels separating post from caption
