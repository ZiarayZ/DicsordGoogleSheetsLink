from __future__ import print_function
import re

#Discord.py API
import discord
from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True

#Google Sheets API
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#Bot Data for Discord.py API
load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))#discord bot token
ADMIN = int(os.getenv('DISCORD_ADMIN'))#my id, so it won't take the pinned google sheets link
CHANN = int(os.getenv('DISCORD_CHANN'))#the id of the channel the pins are in
client = discord.Client()


# The ID and range of a sample spreadsheet.
spreadsheet_id = str(os.getenv('GOOGLES_TOKEN'))
range_name = str(os.getenv('RANGNAM_STRIN'))

#Admin List
Admins = []
with open('admins.txt', 'r') as f:
    for ID in f:
        Admins.append(int(ID.rstrip()))

#Data for Sheets to pull from
messages = []

#handling message data, stripping for columns (i.e. age, gender, height)
def value_assignment(values):
    global messages
    counter = 0
    for message in messages:
        #name
        two_parts = message.split(': ')
        if two_parts[1][0] == '>':
            two_parts[1] = two_parts[1][1:]
        values.append([two_parts[0]])

        #gender checking
        if re.findall('(?:female|Female|Girl|girl|f|F)', two_parts[1]):#female check
            values[counter].append("F")#gender
        elif re.findall('(?:male|Male|Boy|boy|Boi|boi|m|M)', two_parts[1]):#male check
            values[counter].append("M")#gender
        else:#No gender
            values[counter].append(None)#gender

        #age checking
        two_parts_revision1 = re.sub('(?:\d\d\d)', '', two_parts[1])
        two_parts_revision2 = re.sub('(\\d+)\'(\\d+)', '', two_parts_revision1)
        age = re.findall('(?:9[0-9]|[1-8][0-9]|[1-9])', two_parts_revision2)
        if age:
            try:
                values[counter].append(int(age[1]))#checks if there's a second age, sometimes people say "mentally 18, physically 25" we want the second option not the first
            except:
                values[counter].append(int(age[0]))#if not choose the only age
        else:
            values[counter].append(None)#age

        #country checking
        if "from" in two_parts[1].lower():
            third_part = two_parts[1].lower().split("from ")[1]#splits first part of message off
            country = third_part.split(" ")[0]#Splitting rest of message off
            country = country.upper()#capitalize location name
            values[counter].append(country)#country
        else:
            values[counter].append(None)#country

        #height checking
        height = re.findall('(?:250|2[0-4][0-9]|1[0-9]{2})', two_parts[1])#cm
        height1 = re.findall('(?:2.50|2.[0-4][0-9]|1.[0-9]{2})', two_parts[1])#m
        height2 = re.findall('(\\d+)\'(\\d+)', two_parts[1])#feet
        if len(height) > 0:
            values[counter].append(int(height[0]))
        elif len(height1) > 0:
            height1 = height1[0][0] + height1[0][2:]
            values[counter].append(int(height1))
        elif len(height2) > 0:
            convert = int((int(height2[0][0]) + (int(height2[0][1]) / 12))* 30.48)
            values[counter].append(convert)
        else:
            values[counter].append(None)#height

        #Rest of message
        values[counter].append(two_parts[1])
        counter += 1
        try:
            print(values[counter])
        except:
            print("unsupported character detected in this row")
    return values

#letting you know that the bot has come online and it's in these servers
@client.event
async def on_ready():
    print('Bot initialised in:')
    for guild in client.guilds:
        print(f'NAME: {guild}, (ID: {guild.id})')
    

#moved code out of on_ready, so we can add more moderators/admins to txt file from discord
@client.event
async def on_message(ctx):
    global messages
    global channelID
    global Admins
    if 'ctx.execute(' == ctx.content[0:12] and ctx.content[-1] == ')':
        phrase = ctx.content[12:]
        phrase = phrase[:-1]
        if ctx.channel.id == CHANN and phrase == 'order=66':
            #pulls all message objects from channel CHANN's pinned messages
            message_objects = await client.get_channel(CHANN).pins()
            for message in message_objects:
                #checks if message is from me, or is from a moderator/admin
                if message.author.id != ADMIN and message.author.id not in Admins:
                    messages.append(str(message.author.display_name)+': '+str(message.content).rstrip())
                    await message.unpin()
                #if from moderator/admin, will use the last mention as the user's name
                elif message.author.id in Admins and len(message.mentions) > 0:
                    ment = message.mentions
                    context = message.clean_content.replace('@' + ment[-1].display_name, '')
                    messages.append(str(ment[-1].display_name)+': '+str(context).rstrip())
                    await message.unpin()
                else:
                    print('pinned message is by moderator/admin, without a mention')
            await client.logout()
        #add a new admin to txt file list of admins
        if ctx.channel.id == CHANN and len(ctx.mentions) > 0 and ctx.mentions[0].id not in Admins:
            Admins.append(ctx.mentions[0].id)
            with open('admins.txt', 'a') as f:
                f.write('\n' + str(ctx.mentions[0].id))
                f.close()

#my function for updating sheets
def update_sheet(service):
    values = value_assignment([
        
            # Cell values ...
        
        # Additional rows ...
    ])

    #gets all data and gets all rows
    range_names = range_name.split('.')
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_names[0]).execute().get('values', [])

    #gets last row
    new_row_id = len(rows) + 2
    range_name = range_names[1][0] + str(new_row_id) + range_names[1][1:]

    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


#Google's authorization code
def main():
    global range_name
    #Shows basic usage of the Sheets API.
    #Prints values from a sample spreadsheet.
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    #my code here
    service = build('sheets', 'v4', credentials=creds)
    update_sheet(service)

if __name__ == '__main__':
    client.run(TOKEN)#run bot pulling from pins
    main()#look through stored messages and input into spreadsheet
