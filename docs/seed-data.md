# Seed Data

The seed data represents a snapshot of Dunder Mifflin Scranton branch operations.

## Employees (12)

| Employee ID | Name | Persona |
|---|---|---|
| michael-scott | Michael Scott | manager |
| dwight-schrute | Dwight Schrute | sales |
| jim-halpert | Jim Halpert | sales |
| pam-beesly | Pam Beesly | accounting |
| angela-martin | Angela Martin | accounting |
| kevin-malone | Kevin Malone | accounting |
| darryl-philbin | Darryl Philbin | warehouse |
| ryan-howard | Ryan Howard | sales |
| phyllis-vance | Phyllis Vance | sales |
| stanley-hudson | Stanley Hudson | sales |
| creed-bratton | Creed Bratton | warehouse |
| roy-anderson | Roy Anderson | warehouse |

## Customers (10)

Fictional Scranton-area businesses with realistic coordinates:

- Vance Refrigeration
- Lackawanna County Schools
- Scranton Business Park LLC
- Cooper's Seafood House
- The Electric City Trolley
- Poor Richard's Pub
- Steamtown Mall
- Scranton Cultural Center
- Michael's Foot Massage Parlor
- Dunmore High School

## Trucks (3)

- DM-TRUCK-01 — Dwight's Route (warehouse at 41.406, -75.664)
- DM-TRUCK-02 — Roy's Route
- DM-TRUCK-03 — Darryl's Backup

## Packages (13, across all statuses)

| Status | Count |
|---|---|
| order_created | 2 |
| backorder | 1 |
| packaged | 2 |
| ready_for_shipping | 1 |
| in_transit | 2 |
| delivered | 2 |
| cancelled | 1 |
| damaged | 1 |
| returned | 1 |

Each non-order_created package has at least one history entry reflecting its journey.

## Complaints (3)

- 2 open complaints tied to active sales
- 1 closed complaint

## Demo reset

To restore the baseline state:

```bash
curl -X POST http://localhost:8000/demo/reset -H "X-Persona-Id: michael-scott"
```
