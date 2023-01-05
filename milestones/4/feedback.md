# Feedback Parallel Designs

* Presented in clear language, nice slides.
* What GPUs did you use that you mention in your benchmark slide?
* The OI you have computed in your roofline analysis is certainly wrong.  You
  have not motivated how you have computed this number (such a computation is
  required in your final report).  You report 170e6 total number of instructions
  (lets assume these are all float arithmetic) and 110e6 load/store operations
  (x4 byte if these are single precision) then your OI should be somewhere at
  0.4 flop/byte.
* Parallelization approach is OK
