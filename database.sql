CREATE TABLE IF NOT EXISTS `Users` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255),
  `country_code` VARCHAR(255),
  `phone_number` VARCHAR(255) UNIQUE NOT NULL,
  `selected_site` VARCHAR(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `images` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `content` LONGBLOB NOT NULL,
  `content_type` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS `otps` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `phone_number` VARCHAR(15) NOT NULL UNIQUE,
  `otp` VARCHAR(6) NOT NULL,
  `is_verified` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `expires_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
);



CREATE TABLE IF NOT EXISTS `blogs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `author` VARCHAR(100) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

