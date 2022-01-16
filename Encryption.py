from collections import deque
from itertools import cycle, islice

plaintext = ["1001 0100 0110 0110",
             "0010 1001 1100 0010",
             "0101 1100 1110 0010",
             "1001 1100 0010 0111",
             "1011 1101 1101 1111",
             "0001 1101 0001 0011",
             "1110 0001 1100 0011",
             "0011 1110 0000 0010",
             "0101 0011 1101 1011",
             "1100 0010 0111 0100"]

keys = ["1010 0010 0011 1010",
        "1110 1111 0001 1000",]

sbox = [[15, 10, 2, 5, 8, 4, 11, 6, 1, 0, 14, 7, 9, 3, 12, 13],
        [4, 0, 15, 10, 8, 9, 7, 13, 5, 1, 6, 11, 2, 3, 14, 12]]


class WeakCipher:
    def __init__(self, pt_list, key_list, sbox_list):
        self.keys = key_list
        self.plaintext = pt_list
        self.sbox = sbox_list

    def main(self):
        for key in self.keys:
            self.encryption(deque(self.plaintext), key, self.sbox)
        quit(0)

    def encryption(self, ptext, ktext, sbox):
        order = [[3, 1, 4, 2], [1, 3, 2, 4]]
        sbox = cycle(sbox)

        while ptext:
            popped_plain = ptext.popleft()
            p_text = [num for idex, num in sorted(zip(order[0], popped_plain.split(" ")))]
            k_text = [num for idex, num in sorted(zip(order[1], ktext.split(" ")))]

            xor = list(map(lambda nibble: bin(nibble)[2:].zfill(4), [
                int(nib1, 2) ^ int(nib2, 2) for nib1, nib2 in zip(p_text, k_text)]))
            post_sub = [self.sub_box(nibble, next(sbox)) for nibble in xor]

            self.write(popped_plain, xor, ktext, post_sub)

    @staticmethod
    def sub_box(nibble, sbox):
        nested_sbox = [list(islice(sbox, idex, idex + 4))
                       for idex in range(0, len(sbox), 4)]
        x_coord, y_coord = int(nibble[:2], 2), int(nibble[2:], 2)
        return nested_sbox[y_coord][x_coord]

    @staticmethod
    def write(plaintext, ciphertext, key, post_sub):
        with open("Assignment 1.txt", 'a') as file:
            file.write(f"Plaintext: {plaintext} || Ciphertext Post-XOR: {ciphertext} || "
                       f"Key Used: {key} || Ciphertext Post-Substitution: {post_sub}\n")


if __name__ == '__main__':
    enc1 = WeakCipher(plaintext, keys, sbox)
    enc1.main()
