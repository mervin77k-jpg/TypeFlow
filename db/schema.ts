import {sqliteTable,text,integer} from 'drizzle-orm/sqlite-core';
export const accounts=sqliteTable('accounts',{id:text('id').primaryKey(),email:text('email').notNull(),trialStart:integer('trial_start'),sessions:integer('sessions').notNull().default(0),words:integer('words').notNull().default(0),completed:integer('completed').notNull().default(0),lastActivity:integer('last_activity'),suspended:integer('suspended').notNull().default(0)});
export const profiles=sqliteTable('profiles',{id:text('id').primaryKey(),owner:text('owner').notNull(),name:text('name').notNull(),settings:text('settings').notNull()});

