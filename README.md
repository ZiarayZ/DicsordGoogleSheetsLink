# DiscordGoogleSheetsLink
Reads a channel's pinned messages and puts them into a google sheets document.<br />
The discord server's mods used to manually input people's introductions into a spreadsheet, i decided to make a script which does this automatically (since they're lazy about it).<br />
<br />
Python Requirements:<br />
-Python (version 3.6 was tested/used)<br />
-Google Sheets API v4<br />
-Discord.py API v1.5.0<br /><br />
Other Requirements:<br />
-Fill 'admins.txt' with user IDs (these user IDs are of the admins or mods so it knows to ignore them)<br />
-Make sure to get your own 'credentials.json' from Google Sheets API<br />
<br />
.env Setup:<br />
-DISCORD_TOKEN=(discord bot token here)<br />
-DISCORD_ADMIN=(your user ID here)<br />
-DISCORD_CHANN=(the channel ID with pinned messages here)<br />
-GOOGLES_TOKEN=(the google sheets ID here)<br />
-RANGNAM_STRIN=(the range of the sheets here)<br />
<br />The range of the sheets is still hardcoded in, since this was made for a specific spreadsheet with specific columns, rows are automatically handled.<br />
Since rows are automatically handled you only need to change the code in functions:<br />
-'value_assignment(values)', where it reads through the messages and creates a list of 6 items/columns which is stored in the values list<br />
-'update_sheet(service)', where it calls 'value_assignment()' for writing to spreadsheet<br /><br />
An example is put below and within the '.env' file:<br />
'A2:B.A:F'<br /><br /> 'A2:B' means starting from column A row 2, checking all the way to the bottom for only columns A and B
<br /> '.' Splits 'A2:B' from 'A:F', and 'A:F' means starting at the first empty row input data in columns A to F for each new row inputted
