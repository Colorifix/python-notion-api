# from python_notion_api.gdrive import GDrive
from gdrive import GDrive

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

    def test_upload_file(self):
        gfile = self.gdrive.upload_file(
            self.BUFFER,
            self.PARENT_ID,
            self.IMG_FILE
        )
        self.assertEqual(gfile['originalFilename'], self.IMG_FILE)

    def test_find(self):
        gfile = self.gdrive.upload_fig(
            self.BUFFER,
            self.IMG_FILE,
            self.PARENT_ID
        )
        gfile = self.gdrive.find(self.IMG_FILE, self.PARENT_ID)
        self.assertIsNotNone(gfile)

    def test_get_dataframe(self):
        self.DATAFRAME.to_excel(self.DATAFRAME_FILE_PATH, index=False)
        gfile = self.gdrive.upload_file(
            self.DATAFRAME_FILE_PATH,
            self.PARENT_ID,
            self.DATAFRAME_FILE
        )
        dataframe = self.gdrive.get_dataframe(
            self.DATAFRAME_FILE,
            self.PARENT_ID
        )
        self.assertEqual(dataframe.shape, (3, 2))
        os.remove(self.DATAFRAME_FILE_PATH)


if __name__ == '__main__':
    unittest.main()
