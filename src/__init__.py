from TAQAdjust import *
from TAQCleaner import *
import MyDirectories
from FileManager import FileManager
fm = FileManager(MyDirectories.getTAQDir())
adj = TAQAdjust(isquote=True)
adj.adjustData()
