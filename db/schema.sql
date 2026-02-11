-- =========================================================
-- CORE: Lots + alias mapping
-- =========================================================

CREATE TABLE lots (
  lot_id         BIGSERIAL PRIMARY KEY,                -- surrogate PK
  lot_number     VARCHAR(64) NOT NULL,                 -- business identifier
  created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
  notes          TEXT NULL,
  CONSTRAINT uq_lots_lot_number UNIQUE (lot_number)
);

CREATE TABLE lot_aliases (
  lot_alias_id    BIGSERIAL PRIMARY KEY,
  lot_id          BIGINT NOT NULL REFERENCES lots(lot_id) ON DELETE CASCADE,
  lot_number_raw  VARCHAR(128) NOT NULL,
  source_system   VARCHAR(32) NOT NULL,
  source_file     VARCHAR(255) NULL,
  first_seen_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  last_seen_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT ck_lot_aliases_source_system CHECK (source_system IN ('production','quality','shipping')),
  CONSTRAINT uq_lot_aliases_source_raw UNIQUE (source_system, lot_number_raw)
);

CREATE INDEX idx_lot_aliases_lot_id ON lot_aliases(lot_id);
CREATE INDEX idx_lot_aliases_raw ON lot_aliases(lot_number_raw);


-- =========================================================
-- PRODUCTION
-- =========================================================

CREATE TABLE production_lines (
  production_line_id  BIGSERIAL PRIMARY KEY,
  line_name           VARCHAR(64) NOT NULL,
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_production_lines_name UNIQUE (line_name)
);

CREATE TABLE parts (
  part_id        BIGSERIAL PRIMARY KEY,
  part_number    VARCHAR(64) NOT NULL,
  CONSTRAINT uq_parts_part_number UNIQUE (part_number)
);

CREATE TABLE production_runs (
  production_run_id     BIGSERIAL PRIMARY KEY,
  lot_id                BIGINT NOT NULL REFERENCES lots(lot_id) ON DELETE RESTRICT,
  production_line_id    BIGINT NOT NULL REFERENCES production_lines(production_line_id) ON DELETE RESTRICT,
  part_id               BIGINT NULL REFERENCES parts(part_id) ON DELETE SET NULL,

  run_date              DATE NOT NULL,
  shift                 VARCHAR(16) NULL,

  units_planned         INTEGER NOT NULL DEFAULT 0,
  units_actual          INTEGER NOT NULL DEFAULT 0,
  downtime_minutes      INTEGER NOT NULL DEFAULT 0,

  line_issue_flag       BOOLEAN NOT NULL DEFAULT FALSE,
  primary_issue         VARCHAR(255) NULL,
  supervisor_notes      TEXT NULL,

  created_at            TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT ck_prod_units_planned CHECK (units_planned >= 0),
  CONSTRAINT ck_prod_units_actual CHECK (units_actual >= 0),
  CONSTRAINT ck_prod_downtime CHECK (downtime_minutes >= 0)
);

CREATE INDEX idx_production_runs_lot_id ON production_runs(lot_id);
CREATE INDEX idx_production_runs_run_date ON production_runs(run_date);
CREATE INDEX idx_production_runs_line_date ON production_runs(production_line_id, run_date);


-- =========================================================
-- QUALITY / INSPECTIONS
-- =========================================================

CREATE TABLE inspection_records (
  inspection_record_id   BIGSERIAL PRIMARY KEY,
  lot_id                 BIGINT NOT NULL REFERENCES lots(lot_id) ON DELETE RESTRICT,

  inspection_timestamp   TIMESTAMP NOT NULL,
  inspection_type        VARCHAR(32) NULL,
  inspector_name         VARCHAR(128) NULL,

  sample_size            INTEGER NOT NULL DEFAULT 0,
  result_status          VARCHAR(16) NOT NULL,
  notes                  TEXT NULL,

  created_at             TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT ck_inspection_result CHECK (result_status IN ('pass','fail','conditional')),
  CONSTRAINT ck_sample_size CHECK (sample_size >= 0)
);

CREATE INDEX idx_inspections_lot_ts ON inspection_records(lot_id, inspection_timestamp DESC);
CREATE INDEX idx_inspections_result ON inspection_records(result_status);

CREATE TABLE defect_types (
  defect_type_id      BIGSERIAL PRIMARY KEY,
  defect_name         VARCHAR(128) NOT NULL,
  category            VARCHAR(64) NULL,
  severity_default    VARCHAR(16) NULL,
  CONSTRAINT uq_defect_types_name UNIQUE (defect_name),
  CONSTRAINT ck_defect_severity_default CHECK (severity_default IS NULL OR severity_default IN ('minor','major','critical'))
);

CREATE TABLE defect_instances (
  defect_instance_id     BIGSERIAL PRIMARY KEY,
  inspection_record_id   BIGINT NOT NULL REFERENCES inspection_records(inspection_record_id) ON DELETE CASCADE,
  defect_type_id         BIGINT NOT NULL REFERENCES defect_types(defect_type_id) ON DELETE RESTRICT,

  defect_quantity        INTEGER NOT NULL DEFAULT 1,
  severity               VARCHAR(16) NULL,
  notes                  TEXT NULL,

  CONSTRAINT ck_defect_qty CHECK (defect_quantity > 0),
  CONSTRAINT ck_defect_severity CHECK (severity IS NULL OR severity IN ('minor','major','critical'))
);

CREATE INDEX idx_defect_instances_insp ON defect_instances(inspection_record_id);
CREATE INDEX idx_defect_instances_type ON defect_instances(defect_type_id);


-- =========================================================
-- SHIPPING
-- =========================================================

CREATE TABLE customers (
  customer_id      BIGSERIAL PRIMARY KEY,
  customer_name    VARCHAR(255) NOT NULL,
  CONSTRAINT uq_customers_name UNIQUE (customer_name)
);

CREATE TABLE sales_orders (
  sales_order_id       BIGSERIAL PRIMARY KEY,
  sales_order_number   VARCHAR(64) NOT NULL,
  customer_id          BIGINT NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
  CONSTRAINT uq_sales_orders_number UNIQUE (sales_order_number)
);

CREATE TABLE carriers (
  carrier_id      BIGSERIAL PRIMARY KEY,
  carrier_name    VARCHAR(128) NOT NULL,
  CONSTRAINT uq_carriers_name UNIQUE (carrier_name)
);

CREATE TABLE shipments (
  shipment_id         BIGSERIAL PRIMARY KEY,
  sales_order_id      BIGINT NULL REFERENCES sales_orders(sales_order_id) ON DELETE SET NULL,
  ship_date           DATE NOT NULL,

  destination_state   VARCHAR(32) NULL,
  carrier_id          BIGINT NULL REFERENCES carriers(carrier_id) ON DELETE SET NULL,

  bol_number          VARCHAR(64) NULL,
  tracking_number     VARCHAR(128) NULL,

  ship_status         VARCHAR(16) NOT NULL DEFAULT 'On Hold',
  hold_reason         VARCHAR(255) NULL,
  shipping_notes      TEXT NULL,

  created_at          TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT ck_ship_status CHECK (ship_status IN ('Shipped','Partial','On Hold','Cancelled'))
);

CREATE INDEX idx_shipments_ship_date ON shipments(ship_date);
CREATE INDEX idx_shipments_ship_status ON shipments(ship_status);
CREATE INDEX idx_shipments_bol ON shipments(bol_number);

CREATE TABLE shipment_lines (
  shipment_line_id    BIGSERIAL PRIMARY KEY,
  shipment_id         BIGINT NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
  lot_id              BIGINT NOT NULL REFERENCES lots(lot_id) ON DELETE RESTRICT,
  quantity_shipped    INTEGER NOT NULL DEFAULT 0,

  CONSTRAINT ck_quantity_shipped CHECK (quantity_shipped >= 0),
  CONSTRAINT uq_shipment_lines_shipment_lot UNIQUE (shipment_id, lot_id)
);

CREATE INDEX idx_shipment_lines_lot_id ON shipment_lines(lot_id);
CREATE INDEX idx_shipment_lines_shipment_id ON shipment_lines(shipment_id);


-- =========================================================
-- DASHBOARD VIEW (Unified Dashboard)
-- =========================================================

CREATE OR REPLACE VIEW v_lot_dashboard AS
WITH last_inspection AS (
  SELECT
    ir.*,
    ROW_NUMBER() OVER (PARTITION BY ir.lot_id ORDER BY ir.inspection_timestamp DESC) AS rn
  FROM inspection_records ir
),
shipment_rollup AS (
  SELECT
    sl.lot_id,
    MAX(s.ship_date) AS last_ship_date,
    BOOL_OR(s.ship_status IN ('Shipped','Partial')) AS has_shipped,
    BOOL_OR(s.ship_status = 'On Hold') AS has_hold,
    (ARRAY_AGG(s.ship_status ORDER BY s.ship_date DESC))[1] AS latest_ship_status
  FROM shipment_lines sl
  JOIN shipments s ON s.shipment_id = sl.shipment_id
  GROUP BY sl.lot_id
)
SELECT
  l.lot_id,
  l.lot_number,

  pr.run_date,
  pr.shift,
  pl.line_name,
  p.part_number,
  pr.units_planned,
  pr.units_actual,
  pr.downtime_minutes,
  pr.line_issue_flag,
  pr.primary_issue,

  li.inspection_timestamp AS last_inspection_timestamp,
  li.result_status AS last_inspection_result,

  sr.last_ship_date,
  sr.latest_ship_status,
  COALESCE(sr.has_shipped, FALSE) AS has_shipped,
  COALESCE(sr.has_hold, FALSE) AS has_hold,

  CASE
    WHEN li.result_status = 'pass' AND COALESCE(sr.has_hold, FALSE) = FALSE THEN 'GREEN'
    ELSE 'RED'
  END AS compliance_indicator

FROM lots l
LEFT JOIN production_runs pr ON pr.lot_id = l.lot_id
LEFT JOIN production_lines pl ON pl.production_line_id = pr.production_line_id
LEFT JOIN parts p ON p.part_id = pr.part_id
LEFT JOIN last_inspection li ON li.lot_id = l.lot_id AND li.rn = 1
LEFT JOIN shipment_rollup sr ON sr.lot_id = l.lot_id;

