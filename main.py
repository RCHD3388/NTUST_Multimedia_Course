import argparse

from experiments.part1 import run_part1
from experiments.part2 import (
    run_part2_point1,
    run_part2_point2,
    run_part2_point3,
)
from experiments.part3 import (
    run_part3_point1,
    run_part3_point2a,
    run_part3_point3,
)
from experiments.part4 import (
    run_part4_pointA,
    run_part4_pointB,
    run_part4_pointC,
)


def run_part1_all():
    """Run all experiments for Part 1."""
    print("\n=== PART 1 ===")
    run_part1()


def run_part2_all():
    """Run all experiments for Part 2."""
    print("\n=== PART 2 ===")
    run_part2_point1()
    run_part2_point2()
    run_part2_point3()


def run_part3_all():
    """Run all experiments for Part 3."""
    print("\n=== PART 3 ===")
    run_part3_point1()
    run_part3_point2a()
    run_part3_point3()


def run_part4_all():
    """Run all experiments for Part 4."""
    print("\n=== PART 4 ===")
    run_part4_pointA()
    run_part4_pointB()
    run_part4_pointC()


def main():
    """
    Run one assignment part or all Parts 1-4 from the command line.
    """
    parser = argparse.ArgumentParser(
        description="Multimedia Systems Assignment - Parts 1 to 4"
    )

    parser.add_argument(
        "part",
        choices=["part1", "part2", "part3", "part4", "all"],
        help="Choose which assignment part to run.",
    )

    args = parser.parse_args()

    if args.part == "part1":
        run_part1_all()

    elif args.part == "part2":
        run_part2_all()

    elif args.part == "part3":
        run_part3_all()

    elif args.part == "part4":
        run_part4_all()

    elif args.part == "all":
        run_part1_all()
        run_part2_all()
        run_part3_all()
        run_part4_all()


if __name__ == "__main__":
    main()