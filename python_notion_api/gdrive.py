import os
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GDrive():
    def __init__(self, shared_drive=None, folder=None):
        with open(os.environ.get('GDRIVE_CONF', ".config")) as json_file:
            config = json.load(json_file)

        self.gauth = GoogleAuth()
        self.gauth.DEFAULT_SETTINGS["client_config_file"] = \
            config["GDRIVE"]["CLIENT_CONFIG_FILE"]
        self.gauth.LoadCredentialsFile(config["GDRIVE"]["CREDENTIALS"])
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
        self.gauth.SaveCredentialsFile(config["GDRIVE"]["CREDENTIALS"])
        self.gdrive = GoogleDrive(self.gauth)
        self.shared_drive = shared_drive or config["GDRIVE"]["SHARED_DRIVE"]
        self.folder = folder or config["GDRIVE"]["FOLDER"]

    def find(self, name, parent_id):
        item = self.gdrive.ListFile(
                {
                    'q': f"title = '{name}'"
                         f" and trashed=false"
                         f" and '{parent_id}' in parents",
                    'corpora': "teamDrive",
                    'includeItemsFromAllDrives': "true",
                    'supportsAllDrives': "true",
                    'driveId': self.shared_drive,
                }
            ).GetList()
        if len(item) == 0:
            return None
        elif len(item) == 1:
            return item[0]
        else:
            raise f"There all multiples matches for: {name}"

    def upload_file(self, file_path, file_name=None, parent_id=None):
        file_name = file_name or os.path.basename(file_path)
        parent_id = parent_id or self.folder
        gfile = self.find(file_name, parent_id)

        if gfile is None:
            gfile = self.gdrive.CreateFile(
                {
                    'parents': [{
                        'kind': 'drive#folderLink',
                        'teamDriveId': self.shared_drive,
                        'id': parent_id
                    }],
                    'title': file_name
                }
            )
        gfile.SetContentFile(file_path)
        gfile.Upload(param={'supportsTeamDrives': True})
        return gfile
