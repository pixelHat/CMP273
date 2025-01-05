# Application Task Dependencies and StarPU Monitoring
This document provides an overview of the key features and functionalities of the application, focusing on task dependencies and monitoring StarPU actions. Below are detailed descriptions of the various panels and their functionalities.

## Task Dependency Visualization

![Task Dependency Visualization](dark/application-task-deps.png)

When a user clicks on a specific task, the system highlights all tasks that are dependent on it. This feature allows users to easily identify the relationships between tasks and understand the flow of execution, enhancing their ability to manage and optimize task performance.

## StarPU Task Monitoring

![StarPU Tasks Monitoring](dark/starpu-tasks.png)

This panel displays all actions performed by StarPU. By default, only tasks that exceed a duration of 1 millisecond are shown, allowing users to focus on significant tasks. Users have the flexibility to adjust this filter to view tasks of varying durations, providing a customizable monitoring experience.

## Dataset Selection and Analysis
![StarPU Application Panel](dark/starpu_application_panel.png)

In this panel, users can select multiple datasets and view them side by side, column by column. Additionally, users can enable various analytical options to enhance their data analysis:

1. **ABE (Area Bound Exception)**: This feature indicates the minimum time required to execute the code, excluding time lost due to StarPU overhead and memory transfers.
2. **Outliers**: This option highlights tasks that took longer than their counterparts, allowing users to quickly identify performance bottlenecks.
3. **CPU Idleness**: This metric displays the percentage of time that the CPU core was idle, providing insights into CPU utilization and efficiency.

## Task Status Overview

![Submitted and Ready Tasks Panel](dark/submitted-ready-panel.png)

This panel provides a clear overview of the submitted and ready tasks:
- **Submitted Tasks**: These tasks are currently waiting for their dependencies to be resolved before they can be executed.
- **Ready Tasks**: These tasks are fully prepared and can be executed at any moment, allowing for efficient task management and execution.
