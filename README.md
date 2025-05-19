# VirtualSpace File Monitor 🛠️

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## A Proof of Concept (PoC) for VirtualSpace File Monitor

Welcome to the PoC for the VirtualSpace File Monitor, an interactive monitoring tool to track `.exe` file activity on your system, and more usermode activities. 📁🔍

---

## Overview

VirtualSpace File Monitor provides real-time insights into system activity by continuously tracking executable file creations and deletions, window status changes, and process activity. This demonstration highlights VirtualSpace's capability to dynamically monitor critical file interactions and system events.

## Features

* **Real-Time `.exe` File Monitoring**: Monitors creation and deletion of executable files (`.exe`) specifically.
* **Process Tracking**: Detects when processes start and stop, providing visibility into system activity.
* **Window Monitoring**: Reports when windows are minimized or restored, enhancing user interaction insights.

## How It Works

The monitoring system comprises several core components:

* **FileWatcher**: Continuously scans the drive for new `.exe` files being created or deleted.
* **ProcessWatcher**: Tracks active processes, alerting when new processes start or existing ones terminate.
* **WindowWatcher**: Observes window status changes, reporting minimize and restore events.

## Playing Around with It 🧪

Feel free to interact with your system by:

* Adding or removing `.exe` files.
* Opening, minimizing, and restoring windows.
* Starting and stopping processes.

The system will automatically:

* Log and display detailed event reports.
* Provide real-time summaries of system activity.

⚠️ **Alert**: For best results, ensure the VirtualSpace Monitor runs with appropriate permissions to access system directories. This PoC is streamlined for demonstration purposes. Production versions would include enhanced security checks, customizable monitoring paths, and advanced event filtering.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for exploring the VirtualSpace File Monitor PoC! We value your feedback and contributions. 🚀
