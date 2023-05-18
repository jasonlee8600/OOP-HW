class Rectangle:
    def __init__(self, length, width):
        self._length = length
        self._width = width

    def area(self):
        return self._length * self._width

    def perimeter(self):
        return 2 * self._length + 2 * self._width

class Square(Rectangle):
    def __init__(self, length, *args, **kwargs):
        # This creates a new simpler interface for creating a Square while
        # re-using the init from the parent class
        # note that if we were to add a parameter on the parent, we wouldn't
        # need to change anything here because it passes the rest of the args
        # untouched
        super().__init__(length, length, *args, **kwargs)
        # same as...
        super(Square, self).__init__(length, length, *args, **kwargs)

class Triangle(Rectangle):
    # Triangle does not need its own init since the one it inherits from
    # Recangle will work fine so far

    def area(self):
        # overrides area from Rectangle while *also* using the implementation
        # from Rectangle. If we didn't use super(), this would be a recursive call.
        return super().area() / 2
    
class Cube(Square):
    #inherits init from Square and area/perimeter from Rectangle

    def surface_area(self):
        # adding new functionality
        # super isn't needed here since there is no name confusion and area is
        # inherited
        # if this method was named area and replaced the 2d area method, then we
        # would need super().area()
        face_area = self.area()
        return face_area * 6

    def volume(self):
        face_area = self.area()
        return face_area * self._length

