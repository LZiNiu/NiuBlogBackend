-- -----------------------------------------------------
-- Drop existing tables (in reverse dependency order)
-- -----------------------------------------------------
DROP TABLE IF EXISTS `likes`;
DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `post_tags`;
DROP TABLE IF EXISTS `post_categories`;
DROP TABLE IF EXISTS `posts`;
DROP TABLE IF EXISTS `tags`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- Create Table `users`
-- -----------------------------------------------------
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `nickname` VARCHAR(100) NULL,
  `avatar_url` VARCHAR(255) NULL,
  `bio` TEXT NULL,
  `role` ENUM('USER', 'ADMIN', 'SUPERADMIN') NOT NULL DEFAULT 'USER',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC)
);

-- -----------------------------------------------------
-- Create Table `categories`
-- -----------------------------------------------------
CREATE TABLE `categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL,
  `color` VARCHAR(20) NULL,
  `status` BOOLEAN NOT NULL DEFAULT TRUE,
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);

-- -----------------------------------------------------
-- Create Table `tags`
-- -----------------------------------------------------
CREATE TABLE `tags` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `color` VARCHAR(20) NULL,
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);

-- -----------------------------------------------------
-- Create Table `posts`
-- -----------------------------------------------------
CREATE TABLE `posts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `summary` TEXT NULL,
  `cover_image_url` VARCHAR(255) NULL,
  `content_file_path` VARCHAR(500) NOT NULL,
  `author_id` INT NOT NULL,
  `author_name` VARCHAR(100) NULL,
  `status` ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'draft',
  `view_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `like_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `seo_title` VARCHAR(255) NULL,
  `seo_description` VARCHAR(255) NULL,
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_posts_users_idx` (`author_id` ASC)
);

-- -----------------------------------------------------
-- Create Table `post_categories`
-- -----------------------------------------------------
CREATE TABLE `post_categories` (
  `post_id` INT NOT NULL,
  `category_id` INT NOT NULL,
  `order_index` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`post_id`, `category_id`),
  INDEX `fk_post_categories_categories1_idx` (`category_id` ASC),
  INDEX `fk_post_categories_posts1_idx` (`post_id` ASC)
);

-- -----------------------------------------------------
-- Create Table `post_tags`
-- -----------------------------------------------------
CREATE TABLE `post_tags` (
  `post_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  `order_index` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`post_id`, `tag_id`),
  INDEX `fk_post_tags_tags1_idx` (`tag_id` ASC),
  INDEX `fk_post_tags_posts1_idx` (`post_id` ASC)
);

-- -----------------------------------------------------
-- Add Foreign Key Constraints (Logical, as per requirement)
-- These are commented out as you prefer logical foreign keys.
-- You can add them if you decide to enforce them physically.
-- ALTER TABLE `posts` ADD CONSTRAINT `fk_posts_users` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `post_categories` ADD CONSTRAINT `fk_post_categories_posts` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `post_categories` ADD CONSTRAINT `fk_post_categories_categories` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `post_tags` ADD CONSTRAINT `fk_post_tags_posts` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `post_tags` ADD CONSTRAINT `fk_post_tags_tags` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `comments` ADD CONSTRAINT `fk_comments_posts` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `comments` ADD CONSTRAINT `fk_comments_users` FOREIGN KEY (`author_user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `comments` ADD CONSTRAINT `fk_comments_parent` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `likes` ADD CONSTRAINT `fk_likes_posts` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ALTER TABLE `likes` ADD CONSTRAINT `fk_likes_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
