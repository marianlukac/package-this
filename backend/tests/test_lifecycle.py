"""Tests for package lifecycle validation (T144)."""
import pytest

from app.lifecycle.transitions import (
    VALID_TRANSITIONS,
    InvalidTransitionError,
    PackageStatus,
)
from app.lifecycle.validator import LifecycleValidator
from app.models.package import TERMINAL_STATUSES


def test_valid_transitions_defined():
    assert PackageStatus.ORDER_CREATED in VALID_TRANSITIONS
    assert PackageStatus.DELIVERED in VALID_TRANSITIONS  # can return after delivery


def test_normal_lifecycle_forward():
    progression = [
        (PackageStatus.ORDER_CREATED, PackageStatus.PACKAGED),
        (PackageStatus.PACKAGED, PackageStatus.READY_FOR_SHIPPING),
        (PackageStatus.READY_FOR_SHIPPING, PackageStatus.SHIPPED),
        (PackageStatus.SHIPPED, PackageStatus.IN_TRANSIT),
        (PackageStatus.IN_TRANSIT, PackageStatus.DELIVERED),
    ]
    for current, target in progression:
        LifecycleValidator.validate(current, target)  # must not raise


def test_backorder_from_order_created():
    LifecycleValidator.validate(PackageStatus.ORDER_CREATED, PackageStatus.BACKORDER)


def test_backorder_to_packaged():
    LifecycleValidator.validate(PackageStatus.BACKORDER, PackageStatus.PACKAGED)


def test_cancel_from_any_non_terminal():
    non_terminal = [
        PackageStatus.ORDER_CREATED, PackageStatus.PACKAGED,
        PackageStatus.READY_FOR_SHIPPING, PackageStatus.SHIPPED,
    ]
    for status in non_terminal:
        LifecycleValidator.validate(status, PackageStatus.CANCELLED)


def test_backward_transition_raises():
    with pytest.raises(InvalidTransitionError):
        LifecycleValidator.validate(PackageStatus.IN_TRANSIT, PackageStatus.ORDER_CREATED)


def test_terminal_to_any_raises():
    for terminal in TERMINAL_STATUSES:
        with pytest.raises(InvalidTransitionError):
            LifecycleValidator.validate(terminal, PackageStatus.PACKAGED)


def test_is_terminal():
    for terminal in TERMINAL_STATUSES:
        assert LifecycleValidator.is_terminal(terminal)
    assert not LifecycleValidator.is_terminal(PackageStatus.IN_TRANSIT)


def test_same_status_raises():
    with pytest.raises(InvalidTransitionError):
        LifecycleValidator.validate(PackageStatus.SHIPPED, PackageStatus.SHIPPED)
