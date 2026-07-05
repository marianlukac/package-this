from app.models.package import PackageStatus

# Authoritative state machine — every valid (current → next) transition
VALID_TRANSITIONS: dict[str, list[str]] = {
    PackageStatus.ORDER_CREATED: [
        PackageStatus.BACKORDER,
        PackageStatus.PACKAGED,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
    ],
    PackageStatus.BACKORDER: [
        PackageStatus.PACKAGED,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
    ],
    PackageStatus.PACKAGED: [
        PackageStatus.READY_FOR_SHIPPING,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
    ],
    PackageStatus.READY_FOR_SHIPPING: [
        PackageStatus.SHIPPED,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
    ],
    PackageStatus.SHIPPED: [
        PackageStatus.IN_TRANSIT,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
    ],
    PackageStatus.IN_TRANSIT: [
        PackageStatus.DELIVERED,
        PackageStatus.CANCELLED,
        PackageStatus.DAMAGED,
        PackageStatus.RETURNED,
    ],
    # Terminal statuses — no outbound transitions
    PackageStatus.DELIVERED: [
        PackageStatus.RETURNED,
    ],
    PackageStatus.CANCELLED: [],
    PackageStatus.DAMAGED: [],
    PackageStatus.RETURNED: [],
}


class InvalidTransitionError(Exception):
    def __init__(self, current_status: str, target_status: str) -> None:
        self.current_status = current_status
        self.target_status = target_status
        self.message = (
            f"Invalid transition from '{current_status}' to '{target_status}'. "
            f"Allowed transitions: {VALID_TRANSITIONS.get(current_status, [])}"
        )
        super().__init__(self.message)


class MissingLineItemsError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Package must have at least one line item before advancing past 'order_created'."
        )
