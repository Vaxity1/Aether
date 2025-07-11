"""
task_manager.py - Task Management System
Manages dynamic task prioritization and execution.
"""
from typing import Any, Dict, List

def calculate_task_priority(task: Any, context: Any) -> float:
    base_priority = getattr(task, 'importance', 1) * getattr(task, 'urgency', 1)
    complexity_factor = 1.0
    if getattr(context, 'project_complexity', None) == "complex":
        complexity_factor = 1.2
    elif getattr(context, 'project_complexity', None) == "simple":
        complexity_factor = 0.8
    debt_penalty = 1.0 - (getattr(context, 'technical_debt', 0) * 0.1)
    learning_bonus = 1.0
    if getattr(task, 'introduces_new_pattern', False):
        learning_bonus = 1.3
    return base_priority * complexity_factor * debt_penalty * learning_bonus

class TaskManager:
    def __init__(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]):
        self.tasks = tasks
        self.context = context
    def prioritize_tasks(self) -> List[Dict[str, Any]]:
        return sorted(self.tasks, key=lambda t: -calculate_task_priority(t, self.context))
    def execute_tasks(self) -> List[Dict[str, Any]]:
        prioritized = self.prioritize_tasks()
        for task in prioritized:
            task['executed'] = True
        return prioritized

class TaskManagerModule:
    def __init__(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]):
        self.tasks = tasks
        self.context = context
    def prioritize(self) -> List[Dict[str, Any]]:
        try:
            prioritized = sorted(self.tasks, key=lambda t: -calculate_task_priority(t, self.context))
            return prioritized
        except Exception:
            return self.tasks
    def execute(self) -> List[Dict[str, Any]]:
        prioritized = self.prioritize()
        for task in prioritized:
            try:
                task['executed'] = True
            except Exception:
                pass
        return prioritized
