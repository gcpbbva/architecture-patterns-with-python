import os
import shutil


class LocalFileSystem:
    def copy(self, src, dest):
        shutil.copyfile(src, dest)

    def move(self, src, dest):
        shutil.move(src, dest)

    def delete(self, dest):
        os.remove(dest)
