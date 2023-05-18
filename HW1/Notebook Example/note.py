import datetime
from comparable import ComparableMixin

class Note(ComparableMixin):
    """Represent a note in the notebook. Match against a
    string in searches and store tags for each note."""

    # Store the next available id for all new notes
    last_id = 0

    def __init__(self, memo, tags=""):
        """initialize a note with memo and optional
        space-separated tags. Automatically set the note's
        creation date and a unique id."""

        self._memo = memo
        self._tags = tags
        self._creation_date = datetime.date.today()

        Note.last_id += 1
        self._id = Note.last_id


    def matches(self, filter_string):
        """Determine if this note matches the filter
        text. Return True if it matches, False otherwise.

        Search is case sensitive and matches both text and
        tags."""

        return filter_string in self._memo or filter_string in self._tags

    def id_matches(self, id):
        """
        Determine if this note has the given id
        """
        return self._id == int(id)

    def update_memo(self, memo):
        self._memo = memo

    def update_tags(self, tags):
        self._tags = tags

    def __str__(self):
        return f"{self._id}: {self._memo}\n{self._tags}"

    def __lt__(self, other):
        return self._id < other._id

