import random

class TextInfo:
    def __init__(self,text,meta:None):
        self.text=text
        self.meta=meta
        self.signature=random.random()