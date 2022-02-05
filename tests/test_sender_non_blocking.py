from threading import active_count
from time import sleep

from genet.sender import Sender
from genet.receiver import iterate


def generate_lines(filename: str):
    with open(filename, "r") as fichier:
        for ligne in fichier:
            yield ligne.strip()

def generate_kmers(reads, k):
    for read in reads:
        for i in range(len(read) - k + 1):
            yield read[i : i + k]

# TODO why is this one failing ?
# def test_sender_receive_non_blocking():
#     assert active_count() == 1

#     lines = generate_lines("test.txt")
#     print(lines)
#     Sender(("lines", lines))

#     assert active_count() == 2


#     lines = iterate("lines")
#     kmers = generate_kmers(lines, 5)

#     for kmer in kmers:
#         print(kmer)
    


def test_sender_receive_non_blocking():
    assert active_count() == 1

    lines = generate_lines("tests/test.txt")
    Sender(("lines", lines))

    assert active_count() == 2


    lines = iterate("lines")
    kmers = generate_kmers(lines, 5)

    expected_lines = generate_lines("tests/expected.txt")


    for kmer, line in zip(kmers, expected_lines):
        assert kmer == line

    assert active_count() == 2   # TODO wy not 1 ??

