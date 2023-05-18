class ComparableMixin():
    "Assumes that __lt__ is appropriately implemented and derives the remaining comparison methods from these"
    
    def __ge__(self, other) -> bool:
        return not self.__lt__(other)

    def __gt__(self, other) -> bool:
        return other.__lt__(self)

    def __le__(self, other) -> bool:
        return not self.__gt__(other)

    def __eq__(self, other) -> bool:
        return not self.__lt__(other) and not self.__gt__(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

