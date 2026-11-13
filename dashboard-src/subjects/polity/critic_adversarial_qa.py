"""Run source-derived checks; retired hash locks preserved an erroneous parser."""
from validate_polity import validate


def run_critic_pass():
    return validate()


if __name__ == "__main__":
    run_critic_pass()
