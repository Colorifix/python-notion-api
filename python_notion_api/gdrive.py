import os
import warnings

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile

import requests as requests
import pandas as pd
from io import BytesIO
from typing import Union


class GDrive:
    """
    Uses PyDrive for authentication and requests to get the data from the
    sheet.
    """

    _mime_map = {
        "xls": 'application/vnd.ms-excel',
        "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        "xml": 'text/xml',
        "csv": 'text/csv',
        "pdf": 'application/pdf',
        "php": 'application/x-httpd-php',
        "jpg": 'image/jpeg',
        "png": 'image/png',
        "gif": 'image/gif',
        "bmp": 'image/bmp',
        "txt": 'text/plain',
        "doc": 'application/msword',
        "js": 'text/js',
        "swf": 'application/x-shockwave-flash',
        "mp3": 'audio/mpeg',
        "zip": 'application/zip',
        "rar": 'application/rar',
        "tar": 'application/tar',
        "arj": 'application/arj',
        "cab": 'application/cab',
        "html": 'text/html'
    }

    def __init__(self):
        self.gauth = GoogleAuth()

        client_config_file = os.environ['CLIENT_CONFIG_FILE']
        credentials = os.environ['CREDENTIALS']

        self.gauth.DEFAULT_SETTINGS["client_config_file"] = client_config_file
        self.gauth.LoadCredentialsFile(credentials)

        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile(credentials)
        self.gdrive = GoogleDrive(self.gauth)

    def find(self, name: str, parent_id: str) -> Union[None, GoogleDriveFile]:
        """Get a file item from google drive by name and parent ID.
        Returns None if no such files is found and throws an error if there are
        multiple matches.

        Args:
            name: name of file on google drive
            parent_id: id of the parent folder
        """
        item = self.gdrive.ListFile(
                {
                    'q': f"title = '{name}'"
                        f" and trashed=false"
                        f" and '{parent_id}' in parents",
                    'includeItemsFromAllDrives': "true",
                    'supportsAllDrives': "true"
                }
            ).GetList()
        if len(item) == 0:
            return None
        elif len(item) == 1:
            return item[0]
        else:
            raise ValueError(f"There all multiples matches for: {name}")

    def upload_file(
        self,
        file: Union[BytesIO, str],
        parent_id: str,
        file_name: str,
        format: str = "png"
    ):
        """Upload file to google drive.

        Args:
            file: an in memory file or a path to a file
            parent_id: id of the parent folder on google drive
            file_name: name of file on drive
            format: file format. must be supplied if memory file. default 
                is png.
        """
        gfile = self.find(file_name, parent_id)

        if gfile is None:

            data = {
                'parents': [{'id': parent_id}],
                'title': file_name
            }

            if isinstance(file, str):
                gfile = self.gdrive.CreateFile(data)
                gfile.SetContentFile(file)

            else:
                try:
                    data['mimeType'] = self._mime_map[format]
                except KeyError as e:
                    raise KeyError(
                        f"File type {e} is currently not supported for"
                        + "uploading."
                    )
                gfile = self.gdrive.CreateFile(data)
                gfile.content = file

        gfile.Upload()

        return gfile

    def get_dataframe(
        self, sheet_name: str, parent_id: str
    ) -> Union[None, pd.DataFrame]:
        """Gets a googlesheet by name and parent ID and returns it as a pandas
        dataframe. Returns None if no such sheet is found. Only the first sheet
        in an xlsx is returned.

        Args:
            sheet_name: name of the googlesheet file
            parent_id: id of the parent folder
        """

        sheet = self.find(name=sheet_name, parent_id=parent_id)

        if sheet is not None:
            url = "https://docs.google.com/spreadsheets/export?id=" +\
                sheet['id'] + "&exportFormat=csv"

            headers = {
                'Authorization':
                    'Bearer ' + self.gauth.credentials.access_token
            }
            res = requests.get(url, headers=headers)

            if res.status_code != requests.codes.ok:
                res.raise_for_status()

            return pd.read_csv(BytesIO(res.content))

        else:
            return None

    def create_folder(
        self,
        folder_name: str,
        parent_id: str
    ):
        """Creates a folder with the given name inside of the specified
        parent folder. If a folder with the same name already exists, it 
        returns a pointer to it.

        Args:
            folder_name: name of the folder
            parent_id: id of the parent folder
        """
        gfolder = self.find(folder_name, parent_id)
        if gfolder is None:
            gfolder = self.gdrive.CreateFile(
                {
                    'title': folder_name,
                    'mimeType': "application/vnd.google-apps.folder",
                    'parents': [{'id': parent_id}]
                }
            )
            gfolder.Upload()
        return gfolder
