import path_var
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

import os, time
from dateutil import parser, tz
from datetime import datetime

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

global main_folder_id
main_folder_id = path_var.main_folder_id

global main_path
main_path = path_var.main_path

# library to install..
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

class MyDrive():
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
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

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size=10):
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name, mimeType, modifiedTime, trashed)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                # print(item)

    def upload_file(self, filename, path, folder_id):
        media = MediaFileUpload(f"{path}{filename}")

        response = self.service.files().list(
            q=f"name='{filename}' and not trashed and parents='{folder_id}'",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, modifiedTime, trashed)',
            pageToken=None).execute()

        # print("Printing response: ", response)


        if len(response['files']) == 0:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            print(f"A new file was created {file.get('id')}")

        else:
            for file in response.get('files', []):
                # Process change
                online_file_modified_time = file['modifiedTime']
                print("online_file_modified_time :- ", online_file_modified_time)

                # online = parser.isoparse(online_file_modified_time)
                # print("Online:-", online)

                ## Converting string to datetime format
                onlinetime = datetime.strptime(online_file_modified_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                # print(onlinetime)

                ## Converting time zone..
                onlinetime = onlinetime.replace(tzinfo=from_zone)
                # print("Online time UTC zone:- ", onlinetime)
                online = onlinetime.astimezone(to_zone)
                print("Online local zone:-", online)

                

                ## Converting back to string..
                online = online.strftime('%Y-%m-%d %H:%M:%S.%fZ')
                # print("online:-", online)

                # print(time.strptime(online, '%Y-%m-%d %H:%M:%S.%fZ'))

                online = time.mktime(time.strptime(online, '%Y-%m-%d %H:%M:%S.%fZ'))
                print("Online:-", online)


                ## Time calculation for local file..
                local_file_modified_time = time.ctime(os.path.getmtime(os.path.join(path, filename)))
                print("local_file_modified_time :- ", local_file_modified_time)
                local_file_modified_time = os.path.getmtime(os.path.join(path, filename))
                print("local_file_modified_time :- ", local_file_modified_time)


                # print("Type: ", type(online_file_modified_time), type(local_file_modified_time), type(online))

                if(local_file_modified_time > online):
                    update_file = self.service.files().update(
                        fileId=file.get('id'),
                        media_body=media,
                    ).execute()
                    print(f'Updated File')

                else:
                    print("File already up to date.")

    def make_folder(self, new_folder, parent_folder_id):

        ##first searches for the folder, if not present then create the same.....
        print("Searching for the folder in the given directory:-\n")
        response = self.service.files().list(
            q=f"mimeType = 'application/vnd.google-apps.folder' and not trashed and name='{new_folder}' and parents='{parent_folder_id}'",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=None).execute()
        print(response)
        print("Search end.....////////////////\n\n")
        
        if len(response['files']) == 0:
            file_metadata = {
                'name': new_folder,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            file = self.service.files().create(body=file_metadata,
                                            fields='id').execute()
            print('A folder is created with Folder ID: %s' % file.get('id'))
            return file.get('id')
        
        else:
            print("Folder was already present..\n")
            return response['files'][0]['id']

    def backup(self, path, folder_id):
        items = os.listdir(path)
        print("Printing items in Local system:", items)

        for file in items:
            print("\n",file, "\n")
            if os.path.isfile(os.path.join(path, file)):
                self.upload_file(file, path, folder_id)
            else:
                new_folder_id = self.make_folder(file, folder_id)
                new_path = path + file +"/"
                print("New Path: ", new_path)
                self.backup(new_path, new_folder_id)




def main():
    my_drive = MyDrive()
    # print("\nPrinting-----------------------")
    # my_drive.list_files()
    # print("Printing end-----------------------\n\n")

    # folder_id = my_drive.make_folder('Sagar', main_folder_id)
    # print("FOLDER_ID: ", folder_id)

    my_drive.backup(main_path, main_folder_id)


if __name__ == '__main__':
    main()
