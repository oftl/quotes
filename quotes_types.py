class Quote ():

    def __init__ (self, **kwa):
        self._author = kwa.get ('author')
        self._text   = kwa.get ('text')
        self._id     = kwa.get ('id')

    def __repr__ (self):
        return "Quote (author={author}, text={text}, id={id})".format (
            author  = self.author,
            text    = self.text,
            id      = self.id,
        )


    def contains (self, term):
        if term and term in self.text:
            return True

        return False


    @property
    def author (self):
        return self._author

    @author.setter
    def set_author (self, author):
        self._author = author
        return self._author

    @property
    def text (self):
        return self._text

    @text.setter
    def set_text (self, text):
        self._text = text
        return self._text

    @property
    def id (self):
        return self._id

    @id.setter
    def set_id (self, id):
        self._id = id
        return self._id
