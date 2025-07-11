"""
test_task_manager.py - Unit tests for task_manager.py
"""
import unittest
from task_manager import TaskManager, TaskManagerModule
from typing import Any, Dict, List

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.context: Dict[str, Any] = {
            'project_complexity': 'intermediate',
            'technical_debt': 0.2
        }
        self.tasks: List[Dict[str, Any]] = [
            {'name': 'A', 'importance': 2, 'urgency': 2, 'introduces_new_pattern': False},
            {'name': 'B', 'importance': 3, 'urgency': 1, 'introduces_new_pattern': True}
        ]

    def test_prioritize_tasks(self):
        tm = TaskManager(self.tasks, self.context)
        prioritized = tm.prioritize_tasks()
        self.assertEqual(len(prioritized), 2)
        self.assertTrue(prioritized[0]['name'] in ['A', 'B'])

    def test_execute_tasks(self):
        tm = TaskManager(self.tasks, self.context)
        executed = tm.execute_tasks()
        for task in executed:
            self.assertTrue(task['executed'])

    def test_task_manager_module(self):
        tmm = TaskManagerModule(self.tasks, self.context)
        prioritized = tmm.prioritize()
        self.assertEqual(len(prioritized), 2)
        executed = tmm.execute()
        for task in executed:
            self.assertTrue(task['executed'])

if __name__ == "__main__":
    unittest.main()
