/*
Source Server Version : 101000
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 101000
File Encoding         : 65001

Date: 2019-10-15 00:07:36
*/


-- ----------------------------
-- Table structure for conversation
-- ----------------------------
CREATE SEQUENCE IF NOT EXISTS table_conversation_id_seq;

CREATE TABLE IF NOT EXISTS "public"."conversation" (
"conversation_id" int4 DEFAULT nextval('table_conversation_id_seq'::regclass) NOT NULL,
"ticket_id" uuid NOT NULL,
"text" text COLLATE "default" NOT NULL,
"created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP NOT NULL,
"from_user_id" int4 NOT NULL,
"from_support" bool DEFAULT false NOT NULL,
"message_id" int4,
"reply_message_id" int4
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table conversation
-- ----------------------------
ALTER TABLE "public"."conversation" ADD PRIMARY KEY ("conversation_id");
