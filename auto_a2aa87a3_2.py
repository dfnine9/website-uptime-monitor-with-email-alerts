```python
"""
Automated Task Scheduling System

This module implements an intelligent task scheduling system that:
1. Reorders tasks based on priority scores
2. Resolves dependency conflicts using topological sorting
3. Generates time estimates using historical data and heuristics
4. Optimizes schedule to minimize total completion time

The system handles circular dependencies, resource constraints, and provides
detailed scheduling analytics including critical path analysis.
"""

import json
import heapq
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import random


@dataclass
class Task:
    """Represents a schedulable task with priority, dependencies, and timing data."""
    id: str
    name: str
    priority: int  # 1-10, 10 being highest priority
    estimated_hours: float
    dependencies: List[str]  # Task IDs this task depends on
    historical_completions: List[float] = None  # Historical completion times in hours
    assigned_resource: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.historical_completions is None:
            self.historical_completions = []


class SchedulingError(Exception):
    """Custom exception for scheduling-related errors."""
    pass


class TaskScheduler:
    """
    Automated task scheduling system with priority-based reordering,
    dependency resolution, and intelligent time estimation.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.resources: Set[str] = set()
        self.schedule_start = datetime.now()
        self.working_hours_per_day = 8
        self.resource_schedules: Dict[str, List[Tuple[datetime, datetime]]] = defaultdict(list)
        
    def add_task(self, task: Task) -> None:
        """Add a task to the scheduling system."""
        try:
            if task.id in self.tasks:
                raise SchedulingError(f"Task {task.id} already exists")
            self.tasks[task.id] = task
            if task.assigned_resource:
                self.resources.add(task.assigned_resource)
            print(f"Added task: {task.name} (Priority: {task.priority})")
        except Exception as e:
            print(f"Error adding task {task.id}: {e}")
            raise
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        try:
            visited = set()
            rec_stack = set()
            cycles = []
            
            def dfs(task_id: str, path: List[str]) -> bool:
                if task_id in rec_stack:
                    cycle_start = path.index(task_id)
                    cycles.append(path[cycle_start:] + [task_id])
                    return True
                
                if task_id in visited:
                    return False
                
                visited.add(task_id)
                rec_stack.add(task_id)
                path.append(task_id)
                
                if task_id in self.tasks:
                    for dep in self.tasks[task_id].dependencies:
                        if dfs(dep, path.copy()):
                            return True
                
                rec_stack.remove(task_id)
                return False
            
            for task_id in self.tasks:
                if task_id not in visited:
                    dfs(task_id, [])
            
            return cycles
        except Exception as e:
            print(f"Error detecting circular dependencies: {e}")
            return []
    
    def resolve_dependencies(self) -> List[str]:
        """Resolve task dependencies using topological sorting with priority weighting."""
        try:
            # Check for circular dependencies
            cycles = self.detect_circular_dependencies()
            if cycles:
                print(f"Warning: Circular dependencies detected: {cycles}")
                # Break cycles by removing the lowest priority dependency
                for cycle in cycles:
                    min_priority_task = min(cycle, key=lambda tid: self.tasks.get(tid, Task('', '', 0, 0, [])).priority)
                    for task_id in cycle:
                        if task_id in self.tasks and min_priority_task in self.tasks[task_id].dependencies:
                            self.tasks[task_id].dependencies.remove(min_priority_task)
                            print(f"Broke cycle: removed dependency {min_priority_task} from {task_id}")
            
            # Build dependency graph
            in_degree = defaultdict(int)
            graph = defaultdict(list)
            
            for task_id, task in self.tasks.items():
                for dep in task.dependencies:
                    if dep in self.tasks:
                        graph[dep].append(task_id)
                        in_degree[task_id] += 1
                    else:
                        print(f"Warning: Dependency {dep} not found for task {task_id}")
            
            # Initialize all tasks with in-degree 0
            for task_id in self.tasks:
                if task_id not in in_degree:
                    in_degree[task_id] = 0
            
            # Priority queue for tasks with no dependencies (priority-weighted)
            ready_queue = []
            for task_id, degree in in_degree.items():
                if degree == 0:
                    priority_score = -self.tasks[task_id].priority  # Negative for max-heap behavior
                    heapq.heappush(ready_queue, (priority_score, task_id))
            
            sorted_tasks = []
            
            while ready_queue:
                _, current_task = heapq.heappop(ready_queue)
                sorted_tasks.append(current_task)
                
                # Update dependencies
                for dependent in graph[current_task]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        priority_score = -self.tasks[dependent].priority
                        heapq.heappush(ready_queue, (priority_score, dependent))
            
            if len(sorted_tasks) != len(self.tasks):
                remaining = set(self.tasks.keys()) - set(sorted_tasks)
                raise SchedulingError(f"Could not resolve all dependencies. Remaining tasks: {remaining}")
            
            print(f"Dependency resolution complete. Task order: {[self.tasks[tid].name for tid in sorted_tasks]}")
            return sorted_tasks
            
        except Exception as e:
            print(f"Error resolving dependencies: {e}")
            raise
    
    def estimate_task_duration(self, task: Task) -> float:
        """Estimate task duration using historical data and heuristics."""
        try:
            if task.historical_completions:
                # Use statistical analysis of historical data
                historical_mean = statistics.mean(task.historical_completions)
                if len(task.historical_completions) > 2:
                    historical_std = statistics.stdev(task.historical_completions)
                    # Use 80th percentile estimate (mean + 0.84 * std)
                    estimated_duration = historical_mean + 0.84 * historical_std
                else:
                    estimated_duration = historical_mean * 1.2  # Add 20% buffer
            else:
                # Use heuristic-based estimation
                base_estimate = task.estimated_hours
                
                # Adjust based on priority (higher priority tasks often underestimated)
                priority_multiplier = 1.0 + (task.priority - 5) * 0.05
                
                # Adjust based on dependency complexity
                dependency_multiplier = 1.0 + len(task.dependencies) * 0.1
                
                # Add uncertainty buffer
                uncertainty_buffer = 1.2
                
                estimated_duration = base_estimate * priority_multiplier * dependency_multiplier * uncertainty_buffer
            
            # Minimum duration of 0.5 hours
            estimated_duration = max(0.5, estimated_duration)
            
            print(f"Task {task.name}: estimated duration {estimated_duration