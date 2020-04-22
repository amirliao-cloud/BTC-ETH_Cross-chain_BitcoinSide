
#
class FieldElement:
    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} is not in field range 0 to {}'.format(num, prime -1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):
        if type(other) is not type(self):
            other = self.__class__(other, self.prime)
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        if type(other) is not type(self):
            other = self.__class__(other, self.prime)
        if other is None:
            return False
        return self.num != other.num or self.prime != other.prime

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different field')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot substract two numbers in different field')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        #if type(other) is not type(self):
            #other = self.__class__(other, self.prime)
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different field')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self
        result = self.__class__(0, self.prime)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result

    def __pow__(self, exponent, modulo=None):
        n = exponent
        while n < 0:
            n += self.prime - 1
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __mod__(self, other):
        if type(other) is not type(self):
            other = self.__class__(other - 1, self.prime)
        return self.num % other.prime

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot devide two numbers in different field')
        num = (self.num * pow(other.num, other.prime - 2, other.prime)) % self.prime
        return self.__class__(num, self.prime)

if __name__ == '__main__':
    a = FieldElement(7, 13)
    b = FieldElement(6, 13)
    c = a + b
    d = a* b
    e = a / b
    f = a ** (-3)
    print(c)
    print(d)
    print(e)
    print(f)