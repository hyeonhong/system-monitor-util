#!/usr/bin/env python3
import csv

# Google Sheets
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


def upload_sheets(values):
    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    SPREADSHEET_ID = '1hpBoyNNPB-QNWFxYQGs5YqaK6Iz_a2WCUE1HpWNven4'
    RANGE_NAME = 'result.csv!A1:E6'
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated in the tab -- [result.csv]'.format(result.get('updatedCells')))


def main():
    # Build result array
    result = []
    with open("result.csv", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # skipping header, was the plan but..
        # print(header)
        data = [r for r in reader]  # put the terminals in list
        ws1 = next((terminal for terminal in data if terminal[0] == '10.28.7.7'), None)
        ws2 = next((terminal for terminal in data if terminal[0] == '10.28.7.77'), None)
        was1 = next((terminal for terminal in data if terminal[0] == '10.28.7.137'), None)
        was2 = next((terminal for terminal in data if terminal[0] == '10.28.7.197'), None)
        test = next((terminal for terminal in data if terminal[0] == '10.28.3.199'), None)
        # print(ws1, ws2, was1, was2, test, sep='\n')
        result.append(header)  # add header
        result.extend([ws1, ws2, was1, was2, test])
        # data = sorted(data)  # sort by first element(ip_address) of list
        # print('\n'.join(str(v) for v in data))  # print list

    # Upload to Google Sheets
    print('Uploading to Google Sheets...')
    upload_sheets(result)


if __name__ == '__main__':
    main()
