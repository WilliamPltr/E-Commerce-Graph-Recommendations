INSERT INTO customers (id, name, join_date) VALUES
('C1','Alice','2024-01-02') ON CONFLICT (id) DO NOTHING;
INSERT INTO customers (id, name, join_date) VALUES
('C2','Bob','2024-02-11') ON CONFLICT (id) DO NOTHING;
INSERT INTO customers (id, name, join_date) VALUES
('C3','Chloé','2024-03-05') ON CONFLICT (id) DO NOTHING;

INSERT INTO categories (id, name) VALUES
('CAT1','Electronics') ON CONFLICT (id) DO NOTHING;
INSERT INTO categories (id, name) VALUES
('CAT2','Books') ON CONFLICT (id) DO NOTHING;

INSERT INTO products (id, name, price, category_id) VALUES
('P1','Wireless Mouse',29.99,'CAT1') ON CONFLICT (id) DO NOTHING;
INSERT INTO products (id, name, price, category_id) VALUES
('P2','USB-C Hub',49.00,'CAT1') ON CONFLICT (id) DO NOTHING;
INSERT INTO products (id, name, price, category_id) VALUES
('P3','Graph Databases Book',39.00,'CAT2') ON CONFLICT (id) DO NOTHING;
INSERT INTO products (id, name, price, category_id) VALUES
('P4','Mechanical Keyboard',89.00,'CAT1') ON CONFLICT (id) DO NOTHING;

INSERT INTO orders (id, customer_id, ts) VALUES
('O1','C1','2024-04-01T10:15:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO orders (id, customer_id, ts) VALUES
('O2','C2','2024-04-02T12:30:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO orders (id, customer_id, ts) VALUES
('O3','C1','2024-04-05T08:05:00Z') ON CONFLICT (id) DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity) VALUES
('O1','P1',1) ON CONFLICT DO NOTHING;
INSERT INTO order_items (order_id, product_id, quantity) VALUES
('O1','P2',1) ON CONFLICT DO NOTHING;
INSERT INTO order_items (order_id, product_id, quantity) VALUES
('O2','P3',1) ON CONFLICT DO NOTHING;
INSERT INTO order_items (order_id, product_id, quantity) VALUES
('O3','P4',1) ON CONFLICT DO NOTHING;
INSERT INTO order_items (order_id, product_id, quantity) VALUES
('O3','P2',1) ON CONFLICT DO NOTHING;

INSERT INTO events (id, customer_id, product_id, event_type, ts) VALUES
('E1','C1','P3','view','2024-04-01T09:00:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO events (id, customer_id, product_id, event_type, ts) VALUES
('E2','C1','P3','click','2024-04-01T09:01:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO events (id, customer_id, product_id, event_type, ts) VALUES
('E3','C3','P1','view','2024-04-03T16:20:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO events (id, customer_id, product_id, event_type, ts) VALUES
('E4','C2','P2','view','2024-04-03T12:00:00Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO events (id, customer_id, product_id, event_type, ts) VALUES
('E5','C2','P4','add_to_cart','2024-04-03T12:10:00Z') ON CONFLICT (id) DO NOTHING;


