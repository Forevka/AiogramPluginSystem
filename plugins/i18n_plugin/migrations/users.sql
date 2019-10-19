/*
Navicat PGSQL Data Transfer

Source Server         : MyServer
Source Server Version : 101000
Source Database       : users
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 101000
File Encoding         : 65001

Date: 2019-10-19 10:37:33
*/


-- ----------------------------
-- Table structure for users
-- ----------------------------
CREATE TABLE IF NOT EXISTS "public"."users" (
"user_id" int8 NOT NULL,
"lang" varchar(255) COLLATE "default",
"created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD PRIMARY KEY ("user_id");
