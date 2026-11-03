# Thumby Benchmark

> Reference: Thumby Random/Thumby Benchmark/Thumby Benchmark.py

Thumby Benchmark is a performance testing application for the original Thumby hardware. It exercises CPU math, display rendering, text drawing, shapes, and garbage-collection timing to estimate system performance.

## Purpose

This project is meant to benchmark how the device handles common workloads under stress. It is structured as a multi-phase test suite with a splash screen, control inputs, and a summary-style result flow.

## Benchmark phases

The program measures performance across several categories:

- integer math
- floating-point math
- frame-per-second drawing
- large pixel fill operations
- text rendering
- shape drawing
- garbage collection timing

## Implementation details

The script uses dual-core shared memory to run one worker on a second core while the main control loop handles display updates. The code is careful about memory safety and uses defensive guards so one failing phase does not crash the whole benchmark.

> The design explicitly avoids risky allocation inside the hot loop and keeps counters bounded in ways that are safe for the device.

## User flow

- Splash screen plays a looping melody
- User presses A to begin
- Benchmark phases run sequentially
- Results are shown for the measured operations and timing

## Notes

This is a practical test tool rather than a game. It is useful for validating improvements to rendering performance, processor efficiency, and display responsiveness on the Thumby platform.
