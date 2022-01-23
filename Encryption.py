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
        "1110 1111 0001 1000"]

subboxes_main = [[15, 10, 2, 5, 8, 4, 11, 6, 1, 0, 14, 7, 9, 3, 12, 13],
                 [4, 0, 15, 10, 8, 9, 7, 13, 5, 1, 6, 11, 2, 3, 14, 12]]

subboxes_additional_diffusion = [[6, 12, 4, 5, 1, 14, 11, 9, 2, 0, 15, 3, 7, 8, 10, 13],
                                 [1, 2, 15, 11, 14, 7, 4, 10, 5, 3, 6, 8, 2, 9, 13, 12]]


class WeakCipher:
    def __init__(self, pt_list, key_list, sbox_list, sbox_list2):
        self.keys = key_list
        self.plaintext = pt_list
        self.sbox, self.sbox2 = sbox_list, sbox_list2
        self.pt_stack = deque(self.plaintext)
        self.bits_changed = 0

    def main(self):
        for key in self.keys:
            while self.pt_stack:
                popped_plain = self.pt_stack.popleft()
                self.encryption(popped_plain, key, self.sbox)
                self.bits_changed += self.calc_avalanche(popped_plain, key, self.sbox)
            self.pt_stack = deque(self.plaintext)

        return f"Total Number of Changed Bits: {self.bits_changed}\nAvalanche Effect: {self.bits_changed / 5120}"

    def encryption(self, ptext, ktext, sbox, avalanche=False):
        order = [[3, 1, 4, 2], [1, 3, 2, 4]]
        sbox_cycle = cycle(sbox)

        p_text = [nibble for _, nibble in sorted(zip(order[0], ptext.split(" ")))] # Reorder nibbles to make it easier to zip and xor
        k_text = [nibble for _, nibble in sorted(zip(order[1], ktext.split(" ")))]

        word_post_xor = list(map(lambda nibble: bin(nibble)[2:].zfill(4), [        # xor operation
            int(nib1, 2) ^ int(nib2, 2) for nib1, nib2 in zip(p_text, k_text)])) 

        post_sub_digits = [self.sub_box(nibble, next(sbox_cycle)) for nibble in word_post_xor]  # Ciphertext in Decimal Form
        post_sub_binary = [bin(digit)[2:].zfill(4) for digit in post_sub_digits]                # Ciphertext in Binary Form

        if avalanche:
            sbox_cycle2 = cycle(self.sbox2)                                                     # Additional Sbox to increase Avalanche
            post_sub_digits = [self.sub_box(nibble, next(sbox_cycle2)) for nibble in post_sub_binary]
            post_sub_binary = [bin(digit)[2:].zfill(4) for digit in post_sub_digits]

            return post_sub_binary

        self.write(ptext, word_post_xor, ktext, post_sub_digits, post_sub_binary)

    def calc_avalanche(self, ptext, ktext, sbox):
        p_text_list, c_text_list = [ptext], []

        for idex, num in enumerate(ptext):
            if num != " ":
                p_text_list.append(ptext[:idex] + str(1 - int(num)) + ptext[idex + 1:])  # Create a list of all plaintexts with 1 flipped bit

        for plaintxt in p_text_list:
            c_text_list.append(self.encryption(plaintxt, ktext, sbox, True))             # Run each plaintext through encryption function and
                                                                                         # append to list. c_text_list[0] is the original ciphertext
        return self.calc_bits_changed(c_text_list[0], c_text_list[1:])                   # that we compare to calc. avalanche effect

    @staticmethod
    def sub_box(nibble, sbox):
        nested_sbox = [list(islice(sbox, idex, idex + 4))                                # Create nested lists out of sbox, so we can use x/y coords
                       for idex in range(0, len(sbox), 4)]
        x_coord, y_coord = int(nibble[:2], 2), int(nibble[2:], 2)
        return nested_sbox[y_coord][x_coord]

    @staticmethod
    def calc_bits_changed(ciphertext_original, ciphertext_changed):                      # Calculate number of changed bits per plaintext 
        count = 0
        ciphertext_original = "".join(ciphertext_original)

        for list_ciphertext in ciphertext_changed:
            str_ciphertext = "".join(list_ciphertext)
            count += sum(1 for bit1, bit2 in zip(ciphertext_original, str_ciphertext) if bit1 != bit2)
        return count

    @staticmethod
    def write(plaintext, ciphertext, key, post_sub_digits, post_sub_binary):
        with open("Assignment 1.txt", 'a') as file:
            file.write(f"Plaintext: {plaintext} || Key Used: {key} || "
                       f"Ciphertext Post-XOR: {ciphertext}  || Ciphertext Post-Sub (Digits): {post_sub_digits} || "
                       f"Ciphertext Post-Sub (Binary): {post_sub_binary}\n")


if __name__ == '__main__':
    enc1 = WeakCipher(plaintext, keys, subboxes_main, subboxes_additional_diffusion)
    print(enc1.main())
