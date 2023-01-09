from python_notion_api.gdrive import GDrive

import unittest
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


class _TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.gdrive = GDrive()
        cls.PARENT_ID = os.environ['PARENT_ID']
        cls.FOLDER_NAME = "TestFolder"
        cls.DATAFRAME = pd.DataFrame(
            {
                "Test1": [420, 380, 390],
                "Test2": [50, 40, 45]
            }
        )
        cls.DATAFRAME_FILE = "Test.xlsx"
        cls.IMG_FILE = "Test.png"

        wdir = os.path.abspath(os.getcwd())
        cls.DATAFRAME_FILE_PATH = os.path.join(wdir, cls.DATAFRAME_FILE)

        fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 10), dpi=500)
        ax1.bar(
            ["A", "B", "C"],
            [10, 12, 14],
            yerr=[1, 2, 0.5],
            color=["red", "blue", "green"],
            alpha=0.3
        )
        ax2.bar(
            ["A", "B", "C"],
            [10, 12, 14],
            yerr=[1, 2, 0.5],
            color=["yellow", "orange", "pink"],
            alpha=0.3
        )

        cls.BUFFER = BytesIO()
        fig.savefig(cls.BUFFER, format="png")

        cls.extra_setup()

    @classmethod
    def extra_setup(cls):
        pass


class TestGDrive(_TestBase):

    def test_find(self):
        gfile = self.gdrive.add_media(
            file=self.BUFFER,
            file_name=self.IMG_FILE,
            parent_id=self.PARENT_ID
        )
        gfile = self.gdrive.find(self.IMG_FILE, self.PARENT_ID)
        self.assertIsNotNone(gfile)

    def test_upload_file(self):
        gfile = self.gdrive.add_media(
            file=self.BUFFER,
            parent_id=self.PARENT_ID,
            file_name=self.IMG_FILE
        )
        self.assertEqual(gfile['originalFilename'], self.IMG_FILE)

    def test_add_folder(self):
        gfile = self.gdrive.add_media(
            parent_id=self.PARENT_ID,
            file_name=self.FOLDER_NAME
        )
        self.assertIsNotNone(gfile)

    def test_get_dataframe(self):
        self.DATAFRAME.to_excel(self.DATAFRAME_FILE_PATH, index=False)
        gfile = self.gdrive.add_media(
            file=self.DATAFRAME_FILE_PATH,
            parent_id=self.PARENT_ID,
            file_name=self.DATAFRAME_FILE
        )
        dataframe = self.gdrive.get_dataframe(
            self.DATAFRAME_FILE,
            self.PARENT_ID
        )
        self.assertEqual(dataframe.shape, (3, 2))
        os.remove(self.DATAFRAME_FILE_PATH)


if __name__ == '__main__':
    unittest.main()
