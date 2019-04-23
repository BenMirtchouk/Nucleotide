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

![Animation GIF](https://raw.githubusercontent.com/benmirtchouk/Nucleotide/master/algorithm_animation.gif)