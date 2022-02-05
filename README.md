# genet [WIP]
propel your python generators through network

In Python, we are able to chain iterators. Here is a simple example of how generators work:

Lets say you want to retrieve all k-mers (substrings of fixed length k) from every line of a file. You could write:
```python
def generate_lines(filename):
    with open(filename, "r") as fichier:
        for ligne in fichier:
            yield ligne


def generate_kmers(reads, k):
    for read in reads:
        for i in range(len(read) - k + 1):
            yield read[i : i + k]


def main() -> None:
    lines = generate_lines("test.txt")
    kmers = generate_kmers(lines, 10)
    for kmer in kmers:
        print(kmer)


if __name__ == "__main__":
    main()
```

Note that we never keep every k-mer in memory. Rather, each time a new k-mer is printed, it is computed on the fly from a line from the file. Should we reach the end of a line, the generator pattern lets you read another line on the fly from the file and generate k-mer from it.

But what if `generate_kmers` if a very computational heavy function ? Well, wouldn't be nice to have a way to send your `lines` to another computer in a cluster ?

Look no further, here we go!

You just need a client and a server:

the server:
```python
from genet.sender import Sender


def generate_lines(filename: str):
    with open(filename, "r") as fichier:
        for ligne in fichier:
            yield ligne


def main() -> None:
    lines = generate_lines("test.txt")
    Sender(("lines", lines))


if __name__ == "__main__":
    main()
```

the client:
```python
from genet.receiver import iterate


def generate_kmers(reads, k):
    for read in reads:
        for i in range(len(read) - k + 1):
            yield read[i : i + k]


def main() -> None:
    lines = iterate("lines")
    kmers = generate_kmers(lines, 5)

    for kmer in kmers:
        print(kmer)


if __name__ == "__main__":
    main()
```


This lets you share some data between nodes in your cluster, or retrieve data from a sensor and iterate over them on a raspberry pi, etc.