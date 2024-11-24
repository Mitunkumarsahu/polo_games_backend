CREATE TABLE `Users` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255),
  `country_code` VARCHAR(255),
  `phone_number` VARCHAR(255) UNIQUE NOT NULL,
  `selected_site` VARCHAR(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `images` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `content` LONGBLOB NOT NULL,
  `content_type` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `otps` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `phone_number` VARCHAR(15) NOT NULL UNIQUE,
  `otp` VARCHAR(6) NOT NULL,
  `is_verified` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `expires_at` DATETIME DEFAULT CURRENT_TIMESTAMP + INTERVAL 5 MINUTE,
  PRIMARY KEY (`id`)
);



INSERT INTO `Users` (`username`, `country_code`, `phone_number`, `selected_site`) VALUES 
('John Doe', 'US', '1234567890', 'Amazon'),
('Jane Smith', 'IN', '9876543210', 'Flipkart'),
('Alice Johnson', 'UK', '1122334455', 'eBay'),
('Bob Brown', 'AU', '9988776655', 'AliExpress'),
('Charlie Wilson', 'CA', '7766554433', 'Walmart'),
('Diana Prince', 'FR', '6677889900', 'Carrefour');
