# Lab 7: Performance Testing with Apache JMeter

Duration: 2 hours. Work in pairs. Each pair runs its own copy of the
app on its own computer, so every pair measures its own machine and
obtains its own numbers.

## Submission

Commit these two files to your repository root:

| File | Content |
|---|---|
| `pytodo_plan.jmx` | Your JMeter test plan |
| `report.pdf` | Your analysis report, 3 to 4 pages, written from `REPORT_TEMPLATE.md` |

Result files (`*.jtl`) and dashboard folders (`report10`, `report25`, and so on) stay on your computer. The
`.gitignore` in this repository already excludes them.

## Terms used in this lab

| Term | Meaning |
|---|---|
| Virtual user | One thread in JMeter. It behaves like one person using the app. |
| Concurrent users | Virtual users active at the same moment. |
| Throughput | Requests completed per second (requests/s, also written RPS). |
| Latency (response time) | Milliseconds from sending a request to receiving the full reply. |
| Percentile | The 95th percentile is the response time covering 95% of the requests. If it reads 400 ms, 95 of every 100 requests finished in 400 ms or less. |
| Think time | Pause a real person takes between two actions. |
| Ramp-up | Time JMeter takes to start all virtual users. |
| Saturation point | Load level where throughput stops rising and response time or errors start to climb. |
| SLA | Service level agreement, a target the app has to meet. |

The SLA for this lab:

- 95th percentile response time of 500 ms or less
- Error rate of 1% or less

Ramp-up rule for this lab: 5 new users start every second. Ramp-up
seconds = users ÷ 5. For 50 users the ramp-up is 10 seconds.

## 1. One-time setup

### 1.1 Java

Open PowerShell and run:

```powershell
java -version
```

A version number of 8 or higher is enough. If the command is
unknown, install Java 17 (Temurin) from <https://adoptium.net>, then
open a new PowerShell window and run `java -version` again.

### 1.2 JMeter

1. Open <https://jmeter.apache.org/download_jmeter.cgi>.
2. Under Binaries, download `apache-jmeter-5.6.3.zip`.
3. Unzip it to `C:\jmeter`. The folder `C:\jmeter\apache-jmeter-5.6.3\bin` now holds `jmeter.bat`.
4. Double-click `jmeter.bat`. The JMeter window opens. Close it for now.

### 1.3 The app

In PowerShell, inside your repository folder:

```powershell
pip install -r requirements.txt
python app.py
```

The terminal prints `PyTodo performance lab running on http://127.0.0.1:5050`.
Leave this window open for the whole lab.

Open a second PowerShell window and check the app:

```powershell
curl.exe http://127.0.0.1:5050/health
```

The reply is `ok`.

macOS and Linux: use `python3` in place of `python`, `bin/jmeter` in
place of `jmeter.bat`, and `curl` in place of `curl.exe`.

## 2. Part A: Build the test plan in the JMeter window

Open `jmeter.bat`. Build the tree below. Right-click an element, choose
Add, then choose the type.

```
PyTodo Load Test                     (Test Plan)
  HTTP Request Defaults
  HTTP Cookie Manager
  Virtual Users                      (Thread Group)
    Log in once per user             (Once Only Controller)
      Login                          (HTTP Request)
        Status is 200                (Response Assertion)
    View task list                   (HTTP Request)
      Status is 200                  (Response Assertion)
    Create task                      (HTTP Request)
      JSON header                    (HTTP Header Manager)
      Status is 201                  (Response Assertion)
    Think time                       (Uniform Random Timer)
    Summary Report                   (Listener)
    Response Time Graph              (Listener)
    View Results Tree                (Listener, used for debugging only)
```

Steps in order:

1. Click the Test Plan element. Set Name to `PyTodo Load Test`. Choose File, Save Test Plan as, and save `pytodo_plan.jmx` in your repository folder.
2. Right-click the Test Plan, Add, Config Element, HTTP Request Defaults. Set Protocol to `http`, Server Name or IP to `127.0.0.1`, Port Number to `5050`. Every request below inherits these values, so each request needs only a path.
3. Right-click the Test Plan, Add, Config Element, HTTP Cookie Manager. Leave the defaults. This element stores the login cookie for each virtual user.
4. Right-click the Test Plan, Add, Threads (Users), Thread Group. Set these fields:

   | Field | Value |
   |---|---|
   | Name | `Virtual Users` |
   | Number of Threads (users) | `2` |
   | Ramp-up period (seconds) | `1` |
   | Loop Count | tick Infinite |
   | Specify Thread lifetime | tick |
   | Duration (seconds) | `20` |

   These small values are for debugging in Part B. Part C raises them to the real load.
5. Right-click Virtual Users, Add, Logic Controller, Once Only Controller. Set Name to `Log in once per user`.
6. Right-click `Log in once per user`, Add, Sampler, HTTP Request. Set Name to `Login`, Method to `POST`, Path to `/login`. Open the Parameters tab, click Add twice, and enter `username` with value `demo`, then `password` with value `demo1234`. Leave the Encode boxes unticked.
7. Right-click Virtual Users, Add, Sampler, HTTP Request. Set Name to `View task list`, Method to `GET`, Path to `/api/tasks`.
8. Right-click Virtual Users, Add, Sampler, HTTP Request. Set Name to `Create task`, Method to `POST`, Path to `/api/tasks`. Open the Body Data tab and paste this line:

   ```
   {"title": "Load task ${__threadNum}-${__counter(FALSE,)}", "priority": 3, "due_date": "2026-12-31"}
   ```

   `${__threadNum}` is the number of the virtual user. `${__counter(FALSE,)}` is a counter shared by all users. Together they give every task a different title.
9. Right-click `Create task`, Add, Config Element, HTTP Header Manager. Set Name to `JSON header`. Click Add, enter Name `Content-Type` and Value `application/json`.
10. Add one Response Assertion under each of the three requests. Right-click the request, Add, Assertions, Response Assertion. Set these fields:

    | Request | Name | Field to Test | Pattern Matching Rules | Patterns to Test |
    |---|---|---|---|---|
    | Login | `Status is 200` | Response Code | Equals | `200` |
    | View task list | `Status is 200` | Response Code | Equals | `200` |
    | Create task | `Status is 201` | Response Code | Equals | `201` |

    To add a pattern, click Add under Patterns to Test and type the number.
11. Right-click Virtual Users, Add, Timer, Uniform Random Timer. Set Name to `Think time`, Random Delay Maximum to `1000`, Constant Delay Offset to `500`. Each virtual user now pauses between 0.5 and 1.5 seconds before every request.
12. Right-click Virtual Users, Add, Listener, Summary Report.
13. Right-click Virtual Users, Add, Listener, Response Time Graph.
14. Right-click Virtual Users, Add, Listener, View Results Tree.
15. Save with Ctrl+S.

## 3. Part B: Debug run in the JMeter window

The JMeter window is the place to design and debug. Load runs belong to
the command line (Part C).

1. Confirm `python app.py` is still running in its own window.
2. Click the green Start arrow. The run lasts about 20 seconds.
3. Click View Results Tree. Every row has a green tick. Click a `Create task` row, then the Response data tab. The body is the created task in JSON.
4. Click Summary Report. Four rows appear: `Login`, `View task list`, `Create task`, `TOTAL`. The Error % column reads `0.00%` for each row.
5. Click Response Time Graph. In the Settings tab, press Display Graph, then open the Graph tab.

Any red row: open View Results Tree, click the row, and read the
Response data and Response headers tabs.

| Symptom | Fix |
|---|---|
| Response code `Non HTTP response code: ... Connection refused` | Start `python app.py` |
| Response code `401` on View or Create | The login request failed. Check the username and password parameters in `Login` |
| Response code `400` on Create | Check the Body Data line and the JSON header |
| Response code `415` on Create | The JSON header is missing. Confirm it sits under `Create task` |

When all rows are green:

1. Right-click View Results Tree and choose Disable. A disabled element shows in grey. It stays disabled for load runs because it stores every response in memory.
2. Save with Ctrl+S.

## 4. Part C: Load runs on the command line

JMeter's own documentation recommends the command line for load
tests, because the window itself consumes memory and CPU.

### 4.1 Make the load adjustable

Return to the JMeter window and change the Thread Group fields. Type
the text exactly as shown:

| Field | Value |
|---|---|
| Number of Threads (users) | `${__P(users,50)}` |
| Ramp-up period (seconds) | `${__P(rampup,10)}` |
| Duration (seconds) | `${__intSum(${__P(rampup,10)},${__P(hold,90)})}` |

`${__P(users,50)}` reads the property `users` from the command line and
uses 50 when no value is given. The duration is the ramp-up time plus 90
seconds of full load. Save with Ctrl+S and close JMeter.

### 4.2 Four runs

Run each line in the PowerShell window of the repository folder, one
after another. Start with the first two lines of the block. They store the
JMeter path and move to the repository folder.

```powershell
$JM = "C:\jmeter\apache-jmeter-5.6.3\bin\jmeter.bat"
cd C:\path\to\your\repository
```

Run 1, 10 users, ramp-up 2 seconds:

```powershell
curl.exe -X POST http://127.0.0.1:5050/admin/reset
& $JM -n -t pytodo_plan.jmx -l run10.jtl -e -o report10 -Jusers=10 -Jrampup=2
```

Run 2, 25 users, ramp-up 5 seconds:

```powershell
curl.exe -X POST http://127.0.0.1:5050/admin/reset
& $JM -n -t pytodo_plan.jmx -l run25.jtl -e -o report25 -Jusers=25 -Jrampup=5
```

Run 3, 35 users, ramp-up 7 seconds:

```powershell
curl.exe -X POST http://127.0.0.1:5050/admin/reset
& $JM -n -t pytodo_plan.jmx -l run35.jtl -e -o report35 -Jusers=35 -Jrampup=7
```

Run 4, 50 users, ramp-up 10 seconds (the required load):

```powershell
curl.exe -X POST http://127.0.0.1:5050/admin/reset
& $JM -n -t pytodo_plan.jmx -l run50.jtl -e -o report50 -Jusers=50 -Jrampup=10
```

Meaning of each part of the command:

| Part | Meaning |
|---|---|
| `-n` | Non-GUI mode |
| `-t pytodo_plan.jmx` | The test plan to run |
| `-l run50.jtl` | File storing every sample |
| `-e -o report50` | Generate the HTML dashboard into the folder `report50` |
| `-Jusers=50` | Sets the property `users` |

Each run takes about 100 seconds. The terminal prints a progress line
every 30 seconds and ends with `... end of run`. Keep other programs
closed during a run. Browser tabs, video calls, and downloads all use
the same CPU as JMeter and the app.

Repeat a run: delete its result file and dashboard folder first.

```powershell
Remove-Item run50.jtl
Remove-Item -Recurse -Force report50
```

JMeter stops with an error when the dashboard folder already exists
and holds files.

## 5. Part D: Read the results

Open `report50\index.html` in a browser.

### 5.1 Statistics table

On the Dashboard page, the Statistics table has one row per request
and a `Total` row. Copy these columns from the `Total` row of each run
into the results table of your report:

| Column | Report column |
|---|---|
| `#Samples` | Requests |
| `Error %` | Error rate |
| `Average` | Average ms |
| `90th pct`, `95th pct`, `99th pct` | Percentiles ms |
| `Throughput` | Requests/s |

Also read the `Create task` row and the `View task list` row of run 4.
They show the request responsible for the slowdown.

### 5.2 Charts to capture from run 4 (50 users)

Use the Charts menu on the left of the dashboard. Take a screenshot of
each chart and place it in the report.

| Chart | Menu path |
|---|---|
| Response time percentiles | Charts, Over Time, Response Time Percentiles Over Time |
| Error visibility | Charts, Throughput, Codes Per Second |
| Load shape | Charts, Over Time, Active Threads Over Time |

The Codes Per Second chart draws one line for each response code.
Lines for 200 and 201 are successful replies. A line for 503 is the
error count per second. Error rate = errors ÷ total requests, and the
Statistics table prints the same value in `Error %`.

Also capture `Response Time Percentiles Over Time` for run 1 (10 users)
so the report can compare a light load with the heavy load.

## 6. Part E: Write the report

1. Open `REPORT_TEMPLATE.md` and copy its headings into a Word or Google Docs file.
2. Fill every section with your own numbers.
3. Insert the screenshots. Add one sentence under each, giving the reading.
4. Save as PDF (File, Download as PDF in Google Docs, or Save As PDF in Word). Name the file `report.pdf`.
5. Commit `report.pdf` and `pytodo_plan.jmx`.

### Maximum throughput

The maximum throughput of the app is the highest `Throughput` value
from a run where both SLA rules hold: 95th percentile of 500 ms or
less, and error rate of 1% or less. Give the number in requests per
second, name the run it came from, and explain why the higher-load runs
were excluded.

### Optional extra, 5 bonus points

Test one of your own recommendations with a fifth run. Stop the app,
then start it again with a faster storage write:

```powershell
$env:WRITE_DELAY_MS = "20"
python app.py
```

Repeat run 4, saving to `run50b.jtl` and `report50b`. Add a
before-and-after table to the report. Start the app with plain
`python app.py` again afterwards.

## 7. Time plan

| Time | Activity |
|---|---|
| 0:00 to 0:35 | Lecture and live demo |
| 0:35 to 1:20 | Parts A and B |
| 1:20 to 1:45 | Part C and the start of Part D |
| 1:45 to 2:00 | Charts and the first draft of the report |

Finish the report after the session and submit `report.pdf` by the
deadline set by your instructor.

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `java` is unknown | Install Java 17 and open a new PowerShell window |
| `Address already in use` when starting the app | Another copy of `python app.py` is running. Close it, then start again |
| Dashboard folder error | Delete the folder and the `.jtl` file, then run again |
| Error % above 0 at 10 users | Confirm `python app.py` stayed running during the whole run, then repeat the run |
| Dashboard charts are empty | The run stopped early. Run again and wait for `end of run` |
| Run 4 ends with 100% errors | The app stopped, or the reset command failed. Start the app, then repeat |
