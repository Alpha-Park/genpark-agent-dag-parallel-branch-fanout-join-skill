"""
Demonstration of genpark-agent-dag-parallel-branch-fanout-join-skill
"""

from client import ParallelBranchFanoutJoinClient

def main():
    coordinator = ParallelBranchFanoutJoinClient()
    batch_id = "research_swarm_batch_01"

    # Define 3 parallel agent branches
    branches = [
        {"subtask_id": "scrape_competitor_a", "input": {"domain": "competitor-a.com"}},
        {"subtask_id": "scrape_competitor_b", "input": {"domain": "competitor-b.com"}},
        {"subtask_id": "query_patents", "input": {"keywords": "multi-agent consensus"}}
    ]

    coordinator.fanout(batch_id, branches)

    # Simulate subtask execution completion
    coordinator.complete_subtask(batch_id, "scrape_competitor_a", result={"pricing": "$49/mo", "features": ["api", "sync"]})
    coordinator.complete_subtask(batch_id, "scrape_competitor_b", result={"pricing": "$99/mo", "features": ["enterprise", "sso"]})
    coordinator.complete_subtask(batch_id, "query_patents", result={"found_patents": 4})

    # Join results across barrier
    join_state = coordinator.evaluate_join(batch_id)
    print("=== BARRIER JOIN EVALUATED ===")
    print(f"Barrier Reached: {join_state['barrier_reached']}")
    print(f"Overall Status: {join_state['status']}")
    print(f"Aggregated Branches: {list(join_state['aggregated_results'].keys())}")

if __name__ == "__main__":
    main()
