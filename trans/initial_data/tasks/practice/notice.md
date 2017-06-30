# Notice

Each task has an attachment package that you can download from the contest system.

There are some "output-only" tasks, for which:
* The input test cases are given in the attachment package. All you need to do is to submit output files for the given test cases. 
* You may have up to 100 submissions. In each submission, you may submit the output files for any subset of the test cases.

For the other tasks:
* You have to submit exactly one file. The file name is given in the task statement header. 
* The attachment package contains sample graders, sample implementations, and example test cases.
* This file should implement the procedures described in the task statement using the signatures provided in the sample implementations.
* These procedures must behave as described in the task statement.
* You are free to implement other procedures. 
* You may have up to 50 submissions for each task.
* In sample grader inputs, every two consecutive numbers on a single line are separated by a single space, unless another format is explicitly specified.
* Your submissions must not interact in any way with the standard input/output streams or with any other file. In particular, reading anything from the standard input or printing anything to the standard output may result in `Security Violation` as the grading outcome. You may output anything to the standard error stream.


## Conventions

The task statements use generic type names  `bool`, `integer`, `int64`, and `int[]` (array). 

In each of the supported programming languages, the graders use appropriate data types or implementations from that language, as listed below:

Language | `bool` | `integer` | `int64` |  `int[]` | length of array `a`
--- | --- | --- | --- | ---
C++ | `bool` | `int` | `long long` | `std::vector<int>` | `a.size()`
Pascal | `boolean` | `longint` |  `int64` |  `array of longint` | `Length(a)`
Java | `boolean` | `int` | `long` |  `int[]` | `a.length`


## Limits

Task | Time limit | Memory limit
--- | --- | ---
Mountains | 1 second | 256 MB 
Cup | 1 second | 256 MB 
Coins | 1 second | 256 MB 
Sudoku | output-only | output-only

