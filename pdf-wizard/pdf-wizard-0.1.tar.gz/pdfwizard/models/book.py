import logging

class Book:
    infoText = ""
    def __init__(self, title, author, subject, pages, size, filepath):
        self.title = title
        self.author = author
        self.subject = subject
        self.pages = pages
        self.size = size
        self.filepath = filepath

    def printInfo(self):
        print(Book.infoText.format(self.title, self.author, self.subject, self.pages, "{:,}".format(self.size), self.filepath))

    def contains(self, search):
        auth = self.author if self.author else ""
        tit = self.title if self.title else ""
        sub = self.subject if self.subject else ""
        if search in tit or search in auth or search in sub:
            return True
        return False

    def __str__(self):
        formattedSize = "{:,}".format(self.size)
        text = f"""
--------------------------
Title:          {self.title}
Author:         {self.author}
Subject:        {self.subject}
Pages:          {self.pages}
Size:           {formattedSize} Bytes
Filepath:       {self.filepath}"""
        return text
