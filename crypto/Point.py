from crypto.FieldElement import FieldElement

class Point:
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        #the point at infinity (None, None, a, b)
        if self.x is None and self.y is None:
            return
        if self.y ** 2 != self.x ** 3 + a * x + b:
            raise ValueError('({}, {}) is not on the curve'.format(x, y))

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        if other is None:
            return False
        return self.x != other.x or self.y != other.y or self.a != other.a or self.b != other.b

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('Points {}, {} are not on the same curve'.format(self, other))
        # one point at infinity
        if self.x is None:
            return other
        if other.x is None:
            return self
        #two different points
        if self.x != other.x:
            slope = (other.y - self.y)/(other.x - self.x)
            x_3 = slope * slope - self.x - other.x
            y_3 = slope * (self.x - x_3) - self.y
            return __class__(x_3, y_3, self.a, self.b)
        if self == other and self.y != 0:
            slope = (3 * (self.x ** 2) + self.a) / (2 * self.y)
            x_3 = slope ** 2 - 2 * self.x
            y_3 = slope * (self.x - x_3) - self.y
            return __class__(x_3, y_3, self.a, self.b)
        if self == other and self.y == 0 * self.x:
            return __class__(None, None, self.a, self.b)

    def __repr__(self):
        return 'Point ({}, {})'.format(self.x, self.y)

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result

if __name__ == '__main__':
    p1 = Point(-1, -1, 5, 7)
    p2 = Point(-1, -2, 5, 7)
    p3 = p1 + p2
    print(p3)

