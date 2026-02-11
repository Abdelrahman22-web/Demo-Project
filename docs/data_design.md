# data_design.md

## Overview

Operations currently pulls **Production**, **Quality**, and **Shipping** spreadsheets, manually aligns them by **Lot IDs** and **dates**, then aggregates to answer summary questions:

- Which **production lines** had the most issues this week?
- What **defect types** are trending?
- Has a **problematic lot/batch** already shipped?

The main pain point: **Lot IDs are inconsistent across files**, creating double-checking and unreliable results. This design centers the model around a canonical **Lot** key with alias tracking.

---

## Entities and attributes

### 1) Lot
**Purpose:** Canonical batch identity used to join Production ↔ Quality ↔ Shipping.

**Attributes**
- `lot_id` (PK, string) — canonical/normalized lot ID
- `created_at` (datetime, nullable)
- `notes` (text, nullable)

---

### 2) LotAlias
**Purpose:** Tracks raw lot ID variants from each source to fix formatting mismatches.

**Attributes**
- `lot_alias_id` (PK, int)
- `lot_id` (FK → Lot.lot_id)
- `lot_id_raw` (string) — exact value from a spreadsheet
- `source_system` (enum/string: `production`, `quality`, `shipping`)
- `source_file` (string, nullable)
- `first_seen_at` (datetime, nullable)
- `last_seen_at` (datetime, nullable)

---

### 3) ProductionLine
**Purpose:** Master list of lines for grouping weekly issues.

**Attributes**
- `production_line_id` (PK, int)
- `line_name` (string, unique)
- `is_active` (bool)

---

### 4) Part
**Purpose:** Master list of part numbers for production context.

**Attributes**
- `part_id` (PK, int)
- `part_number` (string, unique)

---

### 5) ProductionRun
**Purpose:** Production metrics + line issues tied to a lot.

**Attributes**
- `production_run_id` (PK, int)
- `lot_id` (FK → Lot.lot_id)
- `production_line_id` (FK → ProductionLine.production_line_id)
- `part_id` (FK → Part.part_id)
- `run_date` (date)
- `shift` (string/enum, nullable)
- `units_planned` (int, nullable)
- `units_actual` (int, nullable)
- `downtime_min` (int, nullable)
- `line_issue_flag` (bool, nullable)
- `primary_issue` (string, nullable)
- `supervisor_notes` (text, nullable)

---

### 6) Inspection
**Purpose:** A quality inspection event for a lot (supports multiple per lot).

**Attributes**
- `inspection_id` (PK, int)
- `lot_id` (FK → Lot.lot_id)
- `inspection_datetime` (datetime/date)
- `inspection_type` (string/enum, nullable) — e.g., `incoming`, `in_process`, `final`, `audit`
- `inspector` (string, nullable)
- `sample_size` (int, nullable)
- `result` (string/enum, nullable) — e.g., `pass`, `fail`, `conditional`
- `notes` (text, nullable)

---

### 7) DefectType
**Purpose:** Standard defect taxonomy so “defect trending” is consistent.

**Attributes**
- `defect_type_id` (PK, int)
- `defect_name` (string, unique)
- `category` (string, nullable)
- `severity_default` (string/enum, nullable) — `minor`, `major`, `critical`

---

### 8) DefectInstance
**Purpose:** A defect finding recorded during an inspection.

**Attributes**
- `defect_instance_id` (PK, int)
- `inspection_id` (FK → Inspection.inspection_id)
- `defect_type_id` (FK → DefectType.defect_type_id)
- `defect_qty` (int, default 1)
- `severity` (string/enum, nullable)
- `notes` (text, nullable)

---

### 9) Customer
**Purpose:** Customer dimension for shipping reporting.

**Attributes**
- `customer_id` (PK, int)
- `customer_name` (string, unique)

---

### 10) SalesOrder
**Purpose:** Sales order grouping for shipments.

**Attributes**
- `sales_order_id` (PK, int)
- `sales_order_number` (string, unique)
- `customer_id` (FK → Customer.customer_id)

---

### 11) Carrier
**Purpose:** Carrier dimension for logistics reporting.

**Attributes**
- `carrier_id` (PK, int)
- `carrier_name` (string, unique)

---

### 12) Shipment
**Purpose:** Shipment header (status + logistics attributes).

**Attributes**
- `shipment_id` (PK, int)
- `sales_order_id` (FK → SalesOrder.sales_order_id, nullable)
- `ship_date` (date)
- `destination_state` (string, nullable)
- `carrier_id` (FK → Carrier.carrier_id, nullable)
- `bol_number` (string, nullable)
- `tracking_pro` (string, nullable)
- `ship_status` (string/enum, nullable) — `Shipped`, `Partial`, `On Hold`, `Cancelled`
- `hold_reason` (string, nullable)
- `shipping_notes` (text, nullable)

---

### 13) ShipmentLine
**Purpose:** Join table connecting shipments to lots (supports split shipments cleanly).

**Attributes**
- `shipment_line_id` (PK, int)
- `shipment_id` (FK → Shipment.shipment_id)
- `lot_id` (FK → Lot.lot_id)
- `qty_shipped` (int)

---

## Relationships

### Lot identity + standardization
- **Lot (1) → LotAlias (many)**  
  A single canonical lot can have multiple raw ID variants across different source files.

### Production
- **ProductionLine (1) → ProductionRun (many)**
- **Part (1) → ProductionRun (many)**
- **Lot (1) → ProductionRun (many)**  
  Often 1:1 in practice, but modeled as 1:many to handle corrections/rework logs.

### Quality / Defects
- **Lot (1) → Inspection (many)**
- **Inspection (1) → DefectInstance (many)**
- **DefectType (1) → DefectInstance (many)**

### Shipping
- **Customer (1) → SalesOrder (many)**
- **SalesOrder (1) → Shipment (many)**
- **Carrier (1) → Shipment (many)**
- **Shipment (1) → ShipmentLine (many)**
- **Lot (1) → ShipmentLine (many)**  
  Supports partial or split shipments per lot.

---

## Mermaid ERD

```mermaid
erDiagram
  LOT ||--o{ LOT_ALIAS : has
  PRODUCTION_LINE ||--o{ PRODUCTION_RUN : runs
  PART ||--o{ PRODUCTION_RUN : makes
  LOT ||--o{ PRODUCTION_RUN : produced_as

  LOT ||--o{ INSPECTION : inspected_by
  INSPECTION ||--o{ DEFECT_INSTANCE : finds
  DEFECT_TYPE ||--o{ DEFECT_INSTANCE : categorized_as

  CUSTOMER ||--o{ SALES_ORDER : places
  SALES_ORDER ||--o{ SHIPMENT : fulfilled_by
  CARRIER ||--o{ SHIPMENT : transports
  SHIPMENT ||--o{ SHIPMENT_LINE : contains
  LOT ||--o{ SHIPMENT_LINE : shipped_as

  LOT {
    string lot_id PK
    datetime created_at
    string notes
  }

  LOT_ALIAS {
    int lot_alias_id PK
    string lot_id FK
    string lot_id_raw
    string source_system
    string source_file
    datetime first_seen_at
    datetime last_seen_at
  }

  PRODUCTION_LINE {
    int production_line_id PK
    string line_name
    boolean is_active
  }

  PART {
    int part_id PK
    string part_number
  }

  PRODUCTION_RUN {
    int production_run_id PK
    string lot_id FK
    int production_line_id FK
    int part_id FK
    date run_date
    string shift
    int units_planned
    int units_actual
    int downtime_min
    boolean line_issue_flag
    string primary_issue
    string supervisor_notes
  }

  INSPECTION {
    int inspection_id PK
    string lot_id FK
    datetime inspection_datetime
    string inspection_type
    string inspector
    int sample_size
    string result
    string notes
  }

  DEFECT_TYPE {
    int defect_type_id PK
    string defect_name
    string category
    string severity_default
  }

  DEFECT_INSTANCE {
    int defect_instance_id PK
    int inspection_id FK
    int defect_type_id FK
    int defect_qty
    string severity
    string notes
  }

  CUSTOMER {
    int customer_id PK
    string customer_name
  }

  SALES_ORDER {
    int sales_order_id PK
    string sales_order_number
    int customer_id FK
  }

  CARRIER {
    int carrier_id PK
    string carrier_name
  }

  SHIPMENT {
    int shipment_id PK
    int sales_order_id FK
    date ship_date
    string destination_state
    int carrier_id FK
    string bol_number
    string tracking_pro
    string ship_status
    string hold_reason
    string shipping_notes
  }

  SHIPMENT_LINE {
    int shipment_line_id PK
    int shipment_id FK
    string lot_id FK
    int qty_shipped
  }
