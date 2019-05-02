# Nucleotide

## Problem to be Solved

 - All existing methods of aligning sequences have flaws when it comes to aligning DNA sequences that contain **single nucleotide mutations.**
 - This flaw is called **reference bias.**

## Our Proposed Solution: Graph to Graph
-   Create graphs by aligning pairs of reads 
-   Then align pairs of graphs

### Advantages:

 - Sort “by similarity” → preserve low frequency mutations 
-   Later in the alignment process, make conclusions (using t-tests) whether mutation is machine error or significant
	- Hierarchical alignment of sets of reads

## Basic Example of Algorithm

<p align="center">
<img src="https://raw.githubusercontent.com/benmirtchouk/Nucleotide/master/algorithm_animation.gif" style="width:500px; margin:auto; display:block;" alt="Animation GIF"> 
</p>

## Command Line Usage

```bash
cd code
python Nucleotide.py [-h] [--verbosity VERBOSITY] [-n NSEQS] [--html HTML]
                     [--gephi GEPHI]
                     infile

positional arguments:
  infile                seq input file

optional arguments:
  -h, --help            show this help message and exit
  --verbosity VERBOSITY
                        increase output verbosity
  -n NSEQS, --nseqs NSEQS
                        number of seqs to align, default=all
  --html HTML           html output
  --gephi GEPHI         gephi output
```
