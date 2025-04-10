
--
-- Database: wealthwatcher
--

--
-- Dumping data for table accounts
--

INSERT INTO accounts (account_id, bank_name, account_type, balance, create_time, user_id) VALUES
(5, 'Capital One', 'Asset', 4000.00, '2025-04-05 18:48:58', 1),
(6, 'Capital One', 'Liability', 1500.00, '2025-04-05 18:48:58', 1),
(7, 'Wells Fargo', 'Asset', 5000.00, '2025-04-05 18:48:58', 1),
(8, 'Wells Fargo', 'Liability', 2000.00, '2025-04-05 18:48:58', 1);

--
-- Dumping data for table categories
--

INSERT INTO categories (category_id, category_name, description, user_id) VALUES
(5, 'Snacks', 'Light and crispy snacks for on-the-go munching', 1),
(6, 'Beverages', 'Refreshing drinks including juices and soft drinks', 1),
(7, 'Personal Care', 'Daily essentials like soap, shampoo, and lotion', 1);

--
-- Dumping data for table expenses
--

INSERT INTO expenses (expense_id, amount, description, date, category_id, account_id) VALUES
(5, 12.50, 'Bought snacks and gum', '2025-04-06 01:06:13', 5, 5),
(6, 23.99, 'Shampoo and conditioner', '2025-04-06 01:06:13', 7, 7);

--
-- Dumping data for table savings
--

INSERT INTO savings (savings_id, amount, date, description, category_id, account_id) VALUES
(2, 100.00, '2025-04-10 04:00:00', 'This is for snacks', 5, 7);

--
-- Dumping data for table users
--

INSERT INTO users (user_id, email, password, create_time, role) VALUES
(1, 'test1@mail.com', 'myPassword1\r', '2025-04-05 18:39:59', 'User'),
(2, 'admin@mail.com', 'admin123\r', '2025-04-05 18:39:59', 'Admin'),
(3, 'user@mail.com', '12345user\r', '2025-04-05 18:39:59', 'User');
COMMIT;
