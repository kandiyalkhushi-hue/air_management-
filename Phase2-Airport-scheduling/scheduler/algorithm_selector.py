# scheduler/algorithm_selector.py

from scheduler.algorithms.fcfs import fcfs_scheduling
from scheduler.algorithms.sjf import sjf_scheduling
from scheduler.algorithms.srtf import srtf_scheduling
from scheduler.algorithms.priority import priority_scheduling
from scheduler.algorithms.round_robin import round_robin_scheduling
from scheduler.algorithms.hrrn import hrrn_scheduling
from scheduler.algorithms.mlq import mlq_scheduling
from scheduler.algorithms.mlfq import mlfq_scheduling
from scheduler.algorithms.common import (
    normalize_results,
    prepare_flight
)


SUPPORTED_ALGORITHMS = [
    "FCFS",
    "SJF",
    "SRTF",
    "PRIORITY",
    "ROUND_ROBIN",
    "HRRN",
    "MLQ",
    "MLFQ"
]


def normalize_algorithm(algorithm):
    """
    Normalize algorithm name received from
    frontend/API.
    """

    if not algorithm:
        raise ValueError(
            "Algorithm is required"
        )

    algorithm = algorithm.upper().strip()

    aliases = {
        "RR": "ROUND_ROBIN",
        "ROUNDROBIN": "ROUND_ROBIN",
        "ROUND-ROBIN": "ROUND_ROBIN",
        "PRIORITY_SCHEDULING": "PRIORITY",
        "MULTILEVEL_QUEUE": "MLQ",
        "MULTILEVEL_FEEDBACK_QUEUE": "MLFQ"
    }

    algorithm = aliases.get(
        algorithm,
        algorithm
    )

    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. "
            f"Supported algorithms: "
            f"{', '.join(SUPPORTED_ALGORITHMS)}"
        )

    return algorithm


def run_algorithm(
    algorithm,
    flights,
    time_quantum=3
):
    """
    Run the selected scheduling algorithm.

    Parameters:
        algorithm:
            FCFS, SJF, SRTF, PRIORITY,
            ROUND_ROBIN, HRRN, MLQ, MLFQ

        flights:
            List of flights.

        time_quantum:
            Used only by Round Robin.

    Returns:
        Scheduling result list.
    """

    algorithm = normalize_algorithm(
        algorithm
    )
    flights = [prepare_flight(flight) for flight in flights]

    if algorithm == "FCFS":
        results = fcfs_scheduling(flights)
    elif algorithm == "SJF":
        results = sjf_scheduling(flights)
    elif algorithm == "SRTF":
        results = srtf_scheduling(flights)
    elif algorithm == "PRIORITY":
        results = priority_scheduling(flights)
    elif algorithm == "ROUND_ROBIN":
        results = round_robin_scheduling(
            flights,
            time_quantum=time_quantum
        )
    elif algorithm == "HRRN":
        results = hrrn_scheduling(flights)
    elif algorithm == "MLQ":
        results = mlq_scheduling(flights)
    elif algorithm == "MLFQ":
        results = mlfq_scheduling(flights)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return normalize_results(results, flights)

    # This should never be reached because
    # normalize_algorithm validates it.
    raise ValueError(
        f"Unsupported algorithm: {algorithm}"
    )


def get_supported_algorithms():
    """
    Return all supported algorithms.
    """

    return SUPPORTED_ALGORITHMS.copy()