# bumblebench for jitserver benchmarking
This project runs benchmarks on IBM's OpenJ9 JITServer in the JVM for analysis and potential improvement of the JITServer. This project also contains software to graph and analyse the resulting data of the benchmarks, and scripts to automatically create specific graphs. The benchmarking software uses both [bumblebench](https://github.com/adoptium/bumblebench) and [renaissance](https://renaissance.dev/) to conduct its tests. 

The paper resulting from the preliminary tests with the JITServer's scheduler can be found [here](https://hotinfra24.github.io/papers/hotinfra24-final79.pdf).
