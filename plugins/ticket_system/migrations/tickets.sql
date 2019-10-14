/*
Source Server Version : 101000
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 101000
File Encoding         : 65001

Date: 2019-10-15 00:08:10
*/


-- ----------------------------
-- Table structure for tickets
-- ----------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS "public"."tickets";
CREATE TABLE "public"."tickets" (
"ticket_id" uuid DEFAULT uuid_generate_v4() NOT NULL,
"user_id" int8 NOT NULL,
"created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
"status" int2 DEFAULT 1 NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table tickets
-- ----------------------------
ALTER TABLE "public"."tickets" ADD PRIMARY KEY ("ticket_id");
