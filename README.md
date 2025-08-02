# User mode monitor 🛡️

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

VirtualSpace File Monitor provides real-time insights into system activity by continuously tracking executable file creations and deletions, window status changes, and process activity. This demonstration highlights VirtualSpace's capability to monitor critical file interactions and system events dynamically.

## Features

* **Real-Time `.exe` File Monitoring**: Monitors creation and deletion of executable files (`.exe`) specifically.
* **Process Tracking**: Detects when processes/threads start and stop, providing visibility into system activity.
* **Window Monitoring**: Reports when windows are minimized or restored, enhancing user interaction insights.

## How It Works

The monitoring system comprises several core components:

* **FileWatcher**: Continuously scans the drive for new `.exe` files being created or deleted.
* **ProcessWatcher**: Tracks active processes, alerting when new processes start or existing ones terminate.
* **WindowWatcher**: Observes window status changes, reporting minimize and restore events.

## 🧪 Usage

Feel free to interact with your system by:

* Adding or removing `.exe` files.
* Opening, minimizing, and restoring windows.
* Starting and stopping processes.

The monitor will then automatically:

* Log and display detailed event reports.
* Provide real-time summaries of system activity.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
