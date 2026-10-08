-- Run after schema.sql. Two brands with clearly different policies.

insert into brands (id, name) values (1, 'Aurelle Skincare'), (2, 'HydraPure Bottles');

-- Aurelle: short windows (7-day refund, 48h damage report)
insert into kb_entries (brand_id, category, title, content) values
(1, 'return',       'Return policy',       'Unopened items can be returned within 15 days of delivery. Damaged or broken items must be reported within 48 hours of delivery with a photo of the product and packaging. We then send a free replacement.'),
(1, 'refund',       'Refund policy',       'Refunds are only permitted within 7 days of delivery, to the original payment method, and take 5-7 business days. For damaged items we offer a replacement first; a refund is given only if a replacement is unavailable.'),
(1, 'shipping',     'Shipping policy',     'Delivery takes 3-5 business days. Free shipping on orders above Rs 999. Return shipping is free for damaged items.'),
(1, 'cancellation', 'Cancellation policy', 'Orders can be cancelled only before they are shipped. Once shipped, cancellation is not possible and the customer must use the return policy.');

-- HydraPure: longer windows (30-day refund, 7-day damage report)
insert into kb_entries (brand_id, category, title, content) values
(2, 'return',       'Return policy',       'Returns are accepted within 30 days of delivery if the item is in original condition. Damaged items must be reported within 7 days of delivery with a photo or video of the bottle and packaging.'),
(2, 'refund',       'Refund policy',       'Full refund within 30 days of delivery, processed in 3-5 business days. For items damaged on arrival, the customer can choose a refund or a replacement.'),
(2, 'shipping',     'Shipping policy',     'Delivery takes 5-7 business days. Free shipping on all orders. Return pickups are arranged by us at no cost.'),
(2, 'cancellation', 'Cancellation policy', 'Orders can be cancelled within 24 hours of placing the order, even if the shipping label is already created. After 24 hours the customer must use the return policy.');

insert into customers (id, brand_id, name, email) values
(1, 1, 'Priya Sharma', 'priya@example.com'),
(2, 2, 'Rahul Mehta',  'rahul@example.com');

-- Priya: delivered 1 day ago (inside Aurelle's 48h damage window)
-- Rahul: delivered 20 days ago (outside HydraPure's 7-day damage window, still inside 30-day refund)
insert into orders (id, brand_id, customer_id, product, amount, status, delivered_at) values
(1, 1, 1, 'Vitamin C Serum (30ml glass bottle)', 1299.00, 'delivered', now() - interval '1 day'),
(2, 2, 2, 'Insulated Steel Bottle 1L',           1499.00, 'delivered', now() - interval '20 days');

insert into conversations (id, brand_id, customer_id, order_id) values (1, 1, 1, 1), (2, 2, 2, 2);

insert into messages (conversation_id, sender, body) values
(1, 'customer', 'Hi, I received my order today.'),
(1, 'agent',    'Hello Priya, how can I help you?'),
(1, 'customer', 'My order was delivered but the bottle is broken. What can I do?'),
(2, 'customer', 'My order was delivered but the bottle is broken. What can I do?');

-- keep the id counters in sync since we inserted explicit ids
select setval('brands_id_seq', 2), setval('customers_id_seq', 2), setval('orders_id_seq', 2), setval('conversations_id_seq', 2);
