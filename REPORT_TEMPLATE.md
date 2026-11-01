# Performance Test Report: PyTodo

Names: <name 1>, <name 2>
Date: <date>

Length: 3 to 4 pages. Every number comes from your own runs.

## 1. Test environment

| Item | Value |
|---|---|
| Computer (CPU, RAM) | |
| Operating system | |
| JMeter version | 5.6.3 |
| App settings | default (write delay 60 ms, wait limit 500 ms, 16 threads) |
| Where JMeter and the app ran | both on the same computer |

## 2. Test plan

Describe the virtual user in 3 to 5 sentences: the requests sent, the
order, the think time, the ramp-up rule, and the run length. Mention
the file `pytodo_plan.jmx`.

## 3. Results

Copy the `Total` row of each dashboard.

| Users | Ramp-up (s) | Requests | Requests/s | Average (ms) | 90th (ms) | 95th (ms) | 99th (ms) | Error % |
|---|---|---|---|---|---|---|---|---|
| 10 | 2 | | | | | | | |
| 25 | 5 | | | | | | | |
| 35 | 7 | | | | | | | |
| 50 | 10 | | | | | | | |

Per-request rows from run 4 (50 users):

| Request | Requests/s | Average (ms) | 95th (ms) | Error % |
|---|---|---|---|---|
| View task list | | | | |
| Create task | | | | |

## 4. Graphs

Insert each screenshot with one sentence of reading below it.

- Response Time Percentiles Over Time, run 4 (50 users)
- Response Time Percentiles Over Time, run 1 (10 users)
- Codes Per Second, run 4 (50 users)
- Active Threads Over Time, run 4 (50 users)

## 5. Maximum throughput

Maximum throughput: ______ requests/s, taken from the run with ______ users.

Rule applied: 95th percentile of 500 ms or less and error rate of 1%
or less. Explain in 2 to 3 sentences why the runs with more users are
excluded. Quote their numbers.

## 6. Saturation point

State the number of users where the app begins to saturate. Support
the answer with three figures from the table: throughput, 95th
percentile, and error rate, each at the user count below and above the
saturation point.

## 7. Bottleneck

Name the request responsible for the slowdown. Support the answer with
the per-request table in section 3. Read `app.py` and describe the code
responsible, in 2 to 3 sentences.

## 8. Recommended optimizations

Give three recommendations. Each has a title, the change, and the
expected effect on throughput, response time, or error rate.

| Recommendation | Change | Expected effect |
|---|---|---|
| | | |
| | | |
| | | |

## 9. Limits of this test

Name two limits of the measurements. Examples to consider: where JMeter
ran, the length of each run, and the number of runs per load level.
