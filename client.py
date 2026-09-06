"""
Parallel Branch Fanout and Barrier Join Coordinator.
Zero external dependencies, standard library only.
"""

from typing import Dict, List, Any, Optional

class ParallelBranchFanoutJoinClient:
    """
    Coordinates asynchronous branch execution and synchronization:
    - Splits parent tasks into multiple parallel branches (fanout)
    - Records individual branch results with fault containment
    - Enforces barrier synchronization before releasing joined state
    """

    def __init__(self):
        self.batches: Dict[str, Dict[str, Any]] = {}

    def fanout(self, batch_id: str, subtask_definitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Registers a set of parallel branches under a batch barrier."""
        tasks = {}
        for item in subtask_definitions:
            tid = item["subtask_id"]
            tasks[tid] = {
                "subtask_id": tid,
                "input": item.get("input", {}),
                "status": "PENDING",
                "result": None,
                "error": None
            }

        self.batches[batch_id] = {
            "batch_id": batch_id,
            "total_tasks": len(subtask_definitions),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "tasks": tasks
        }
        return {"batch_id": batch_id, "branch_count": len(subtask_definitions), "status": "WAITING_BARRIER"}

    def complete_subtask(self, batch_id: str, subtask_id: str, result: Any, error: Optional[str] = None):
        """Records completion or failure of an individual branch."""
        batch = self.batches.get(batch_id)
        if not batch or subtask_id not in batch["tasks"]:
            raise KeyError(f"Subtask '{subtask_id}' in batch '{batch_id}' not found.")

        task = batch["tasks"][subtask_id]
        if error:
            task["status"] = "FAILED"
            task["error"] = error
            batch["failed_tasks"] += 1
        else:
            task["status"] = "SUCCESS"
            task["result"] = result
            batch["completed_tasks"] += 1

    def evaluate_join(self, batch_id: str) -> Dict[str, Any]:
        """Evaluates barrier condition and merges all branch results."""
        batch = self.batches.get(batch_id)
        if not batch:
            raise KeyError(f"Batch '{batch_id}' not found.")

        total = batch["total_tasks"]
        finished = batch["completed_tasks"] + batch["failed_tasks"]

        if finished < total:
            return {
                "barrier_reached": False,
                "status": "IN_PROGRESS",
                "progress": f"{finished}/{total}"
            }

        # Merge results
        aggregated = {}
        for tid, tmeta in batch["tasks"].items():
            aggregated[tid] = {
                "status": tmeta["status"],
                "result": tmeta["result"],
                "error": tmeta["error"]
            }

        status = "COMPLETED" if batch["failed_tasks"] == 0 else "PARTIAL_FAILURE"
        return {
            "barrier_reached": True,
            "status": status,
            "completed_count": batch["completed_tasks"],
            "failed_count": batch["failed_tasks"],
            "aggregated_results": aggregated
        }
