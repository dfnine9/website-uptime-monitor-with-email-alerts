```python
"""
Task Priority Scoring Algorithm

This module implements a comprehensive priority scoring system that evaluates tasks
based on multiple weighted criteria:
- Deadline urgency (time sensitivity)
- Dependency chains (blocking other tasks)
- Estimated effort (resource requirements)
- Importance levels (business/strategic value)

The algorithm calculates numerical priority scores to help with task scheduling
and resource allocation decisions.
"""

import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Task:
    """Represents a task with priority scoring attributes."""
    id: str
    name: str
    deadline: datetime.datetime
    importance: int  # 1-5 scale (5 = critical)
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    priority_score: float = 0.0


class PriorityScorer:
    """Calculates priority scores for tasks using weighted criteria."""
    
    def __init__(self, 
                 deadline_weight: float = 0.3,
                 dependency_weight: float = 0.25,
                 effort_weight: float = 0.2,
                 importance_weight: float = 0.25):
        """
        Initialize scorer with configurable weights.
        
        Args:
            deadline_weight: Weight for deadline urgency (0-1)
            dependency_weight: Weight for dependency impact (0-1)
            effort_weight: Weight for effort consideration (0-1)
            importance_weight: Weight for business importance (0-1)
        """
        # Normalize weights to sum to 1.0
        total = deadline_weight + dependency_weight + effort_weight + importance_weight
        self.deadline_weight = deadline_weight / total
        self.dependency_weight = dependency_weight / total
        self.effort_weight = effort_weight / total
        self.importance_weight = importance_weight / total
    
    def calculate_deadline_score(self, task: Task) -> float:
        """Calculate urgency score based on deadline proximity."""
        try:
            now = datetime.datetime.now()
            time_diff = (task.deadline - now).total_seconds()
            
            if time_diff <= 0:
                return 1.0  # Overdue tasks get max urgency
            
            days_remaining = time_diff / (24 * 3600)
            
            # Exponential decay: more urgent as deadline approaches
            if days_remaining <= 1:
                return 0.9
            elif days_remaining <= 3:
                return 0.8
            elif days_remaining <= 7:
                return 0.6
            elif days_remaining <= 14:
                return 0.4
            elif days_remaining <= 30:
                return 0.2
            else:
                return 0.1
                
        except Exception as e:
            print(f"Error calculating deadline score for task {task.id}: {e}")
            return 0.5  # Default score on error
    
    def calculate_dependency_score(self, task: Task, all_tasks: Dict[str, Task]) -> float:
        """Calculate score based on dependency chain impact."""
        try:
            # Score based on how many tasks depend on this one
            dependent_count = len(task.dependents)
            
            # Also consider dependency depth (how many tasks this blocks transitively)
            total_blocked = self._count_transitive_dependents(task.id, all_tasks, set())
            
            # Normalize score: more dependents = higher priority
            if total_blocked == 0:
                return 0.1
            elif total_blocked <= 2:
                return 0.3
            elif total_blocked <= 5:
                return 0.6
            elif total_blocked <= 10:
                return 0.8
            else:
                return 1.0
                
        except Exception as e:
            print(f"Error calculating dependency score for task {task.id}: {e}")
            return 0.5
    
    def _count_transitive_dependents(self, task_id: str, all_tasks: Dict[str, Task], visited: set) -> int:
        """Recursively count all tasks that transitively depend on this task."""
        if task_id in visited or task_id not in all_tasks:
            return 0
            
        visited.add(task_id)
        task = all_tasks[task_id]
        count = len(task.dependents)
        
        for dependent_id in task.dependents:
            count += self._count_transitive_dependents(dependent_id, all_tasks, visited)
            
        return count
    
    def calculate_effort_score(self, task: Task) -> float:
        """Calculate score based on estimated effort (inverse relationship)."""
        try:
            # Smaller tasks get higher priority for quick wins
            if task.estimated_hours <= 1:
                return 0.9  # Quick wins
            elif task.estimated_hours <= 4:
                return 0.7
            elif task.estimated_hours <= 8:
                return 0.5
            elif task.estimated_hours <= 16:
                return 0.3
            else:
                return 0.1  # Large tasks get lower priority
                
        except Exception as e:
            print(f"Error calculating effort score for task {task.id}: {e}")
            return 0.5
    
    def calculate_importance_score(self, task: Task) -> float:
        """Calculate score based on business importance level."""
        try:
            # Direct mapping of importance level (1-5) to score (0.2-1.0)
            return min(max(task.importance, 1), 5) * 0.2
        except Exception as e:
            print(f"Error calculating importance score for task {task.id}: {e}")
            return 0.5
    
    def calculate_priority_score(self, task: Task, all_tasks: Dict[str, Task]) -> float:
        """Calculate overall priority score using weighted criteria."""
        try:
            deadline_score = self.calculate_deadline_score(task)
            dependency_score = self.calculate_dependency_score(task, all_tasks)
            effort_score = self.calculate_effort_score(task)
            importance_score = self.calculate_importance_score(task)
            
            total_score = (
                deadline_score * self.deadline_weight +
                dependency_score * self.dependency_weight +
                effort_score * self.effort_weight +
                importance_score * self.importance_weight
            )
            
            return round(total_score, 3)
            
        except Exception as e:
            print(f"Error calculating priority score for task {task.id}: {e}")
            return 0.5
    
    def score_tasks(self, tasks: List[Task]) -> List[Task]:
        """Score all tasks and return them sorted by priority."""
        try:
            # Create lookup dictionary
            task_dict = {task.id: task for task in tasks}
            
            # Build dependency relationships
            for task in tasks:
                for dep_id in task.dependencies:
                    if dep_id in task_dict:
                        task_dict[dep_id].dependents.append(task.id)
            
            # Calculate scores
            for task in tasks:
                task.priority_score = self.calculate_priority_score(task, task_dict)
            
            # Sort by priority score (highest first)
            return sorted(tasks, key=lambda t: t.priority_score, reverse=True)
            
        except Exception as e:
            print(f"Error scoring tasks: {e}")
            return tasks


def create_sample_tasks() -> List[Task]:
    """Create sample tasks for demonstration."""
    now = datetime.datetime.now()
    
    return [
        Task(
            id="T001",
            name="Fix critical security vulnerability",
            deadline=now + datetime.timedelta(days=1),
            importance=5,
            estimated_hours=3,
            dependencies=[]
        ),
        Task(
            id="T002",
            name="Database migration prep",
            deadline=now + datetime.timedelta(days=7),
            importance=4,
            estimated_hours=12,
            dependencies=[]
        ),
        Task(
            id