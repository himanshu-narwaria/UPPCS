"""Audit only active Polity artifacts; shared dashboard checks run separately."""
from validate_polity import validate


if __name__ == "__main__":
    validate()
