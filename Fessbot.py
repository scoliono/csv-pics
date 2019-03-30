# Google Spreadsheet Picture Generator
import pickle
from PIL import Image, ImageFont, ImageDraw
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import Config

def gen_image(quote, author):
    image = Image.new('RGBA', Config.DIM, Config.SECONDARY_COLOR)
    draw = ImageDraw.Draw(image)
    fontsize = Config.FONT_SIZE
    loop = True
    while loop:
        # add newlines to quote to fit it to dimensions
        quote_newlines = ''
        i = 0
        font = ImageFont.truetype(Config.FONT_PATH, fontsize)
        print('attempting font size: {}px'.format(fontsize))
        while i < len(quote):
            next_space = len(quote) if quote.find(' ', i + 1) == -1 else quote.find(' ', i + 1) + 1
            current_word = quote[i:next_space]
            w, h = draw.textsize(quote_newlines + current_word, font=font)
            if w > Config.BOX[2]:
                quote_newlines += '\n'
            quote_newlines += current_word
            i += len(current_word)
        w_author, h_author = draw.textsize(author, font=font)
        # attempt to vertically center. if it still doesn't fit, resize font and try again
        y_quote = int((Config.DIM[1] - h_author - h - Config.GAP_HEIGHT) / 2)
        if h_author + h + Config.GAP_HEIGHT > Config.BOX[3] and fontsize >= 8:
            fontsize -= 4
        else:
            loop = False 
    draw.multiline_text((Config.BOX[0], y_quote), quote_newlines, font=font, fill=Config.PRIMARY_COLOR)
    # x_author = Config.DIM[0] - Config.BOX[0] - w_author - 5
    # ^ only used if we right-align author text - apparently not
    draw.text((Config.BOX[0], min(y_quote + h + Config.GAP_HEIGHT, Config.DIM[1] - Config.GAP_HEIGHT)), author, font=font, fill=Config.PRIMARY_COLOR)
    print('done')
    return image

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', Config.SCOPES
            )
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    sheet = service.spreadsheets()
    row_count = sheet.get(
        spreadsheetId=os.environ.get('SPREADSHEET_ID', Config.SPREADSHEET_ID),
        fields='sheets/properties/gridProperties/rowCount'
    ).execute()['sheets'][0]['properties']['gridProperties']['rowCount']
    print('Spreadsheet has {} rows'.format(row_count))
    result = sheet.values().get(
        spreadsheetId=os.environ.get('SPREADSHEET_ID', Config.SPREADSHEET_ID),
        range=Config.SPREADSHEET_RANGE_FORMAT.format(row_count)
    ).execute()
    values = result.get('values', [])
    if not values:
        print('Nothing found')
    else:
        print('Dumping confessions')
        i = 0
        if os.path.exists('.uploadProgress'):
            with open('.uploadProgress', 'r') as file:
                resume = int(file.readline())
        else:
            resume = 0
        for row in values:
            i += 1
            if not row[0]:
                continue
            author_str = ((row[1] + (', ' if len(row) >= 3 and row[1] else '')) if len(row) >= 2 else '') + (row[2] if len(row) >= 3 else '')
            author_str = author_str if author_str else 'Anonymous'
            print('Starting image #{}'.format(i))
            # don't re-generate any existing image files
            filename = '{}.png'.format(i)
            if not os.path.isfile(filename):
                img = gen_image(row[0], '-' + author_str)
                img.save(filename)
            # Upload to GDrive
            if i > resume:
                metadata = {
                    'name': filename,
                    'parents': [os.environ.get('DEST_ID', Config.DEST_ID)]
                }
                media = MediaFileUpload(filename, mimetype='image/png', resumable=True)
                file = drive_service.files().create(body=metadata, media_body=media, fields='id').execute()
                print('Successfully uploaded: ID {}'.format(file.get('id')))
                with open('.uploadProgress', 'w') as file:
                    file.write(str(i))

if __name__ == '__main__':
    main()
