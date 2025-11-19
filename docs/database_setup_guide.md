# Database Setup Guide

This guide explains how to set up and manage the database for Materials Hub using the Rosemary CLI commands.

## Available Commands

### 1. `rosemary db:setup` - Initial Database Setup

**Use this when:** You're setting up the project for the first time after cloning the repository.

This command will:
- Run all database migrations to create tables
- Populate the database with seed data

```bash
rosemary db:setup
```

To skip the confirmation prompt:
```bash
rosemary db:setup -y
```

**Example output:**
```
Starting database setup...

[1/2] Running database migrations...
Migrations completed successfully.

[2/2] Seeding database with test data...
UserSeeder performed.
DataSetSeeder performed.
...
Database populated with test data.

Database setup completed successfully!
You can now run the application with 'flask run' or 'rosemary run'.
```

---

### 2. `rosemary db:seed` - Populate Database with Data

**Use this when:** You need to add seed data to existing tables (tables already exist).

This command will:
- Load and run all seeders from each module
- Populate tables with test data

```bash
rosemary db:seed
```

**Seed a specific module only:**
```bash
rosemary db:seed auth
```

**Reset database before seeding:**
```bash
rosemary db:seed --reset
```

To skip confirmation prompts:
```bash
rosemary db:seed -y
```

---

### 3. `rosemary db:reset` - Reset Database

**Use this when:** You need to clear all data and start fresh, or rebuild the database from scratch.

This command will:
- Delete all data from all tables
- Clear the uploads folder
- Optionally clear and recreate migrations

```bash
rosemary db:reset
```

**Reset and recreate migrations from scratch:**
```bash
rosemary db:reset --clear-migrations
```

To skip the confirmation prompt:
```bash
rosemary db:reset -y
```

---

### 4. `rosemary db:status` - Database Status

**Use this when:** You want to check the current state of your database.

This command will display:
- Database connection status
- Current migration revision
- Pending migrations (if any)
- Number of tables
- Database size
- Database engine information

```bash
rosemary db:status
```

**Example output:**
```
=== Database Status ===

  Connection: ✓ Connected to 'uvlhubdb'
  Migration: 003abc1234 (current)
  Pending:   ✓ No pending migrations
  Tables:    20
  Size:      0.70 MB
  Engine:    mysql (pymysql)

  Last checked: 2025-01-19 19:36:13
```

This is useful for:
- Quick health check of your database
- Verifying migrations are up to date
- Checking if database is properly configured

---

### 5. `rosemary db:migrate "message"` - Create Migration

**Use this when:** You've made changes to your models and need to create a migration file.

This command will:
- Verify database connection
- Detect changes in your models
- Generate a migration file automatically
- Validate the migration file

```bash
rosemary db:migrate "add csv_file_path to materials"
```

**Example output:**
```
=== Creating New Migration ===

[1/4] Checking database connection... ✓
[2/4] Analyzing model changes...
[3/4] Generating migration file...
  → Detected: Added column 'csv_file_path' to 'materials_dataset'
  Created: migrations/versions/004_add_csv_file_path_to_materials.py
[4/4] Validating migration file... ✓

Migration created successfully!

Next steps:
  1. Review the migration file in migrations/versions/
  2. Run rosemary db:upgrade to apply it
  3. Test the migration in a safe environment first
```

**Advantages over `flask db migrate`:**
- Validates database connection first
- Shows detected changes clearly
- Better error messages
- Tells you what to do next

---

### 6. `rosemary db:upgrade` - Apply Migrations

**Use this when:** You have pending migrations to apply to your database.

This command will:
- Verify database connection
- Check for pending migrations
- Create automatic backup (unless --no-backup)
- Apply all pending migrations
- Verify migration state

```bash
rosemary db:upgrade
```

**Skip automatic backup (not recommended):**
```bash
rosemary db:upgrade --no-backup
```

**Example output:**
```
=== Upgrading Database ===

[1/5] Checking database connection... ✓
[2/5] Checking for pending migrations...
  Found pending migrations
[3/5] Creating backup... ✓
  Backup saved: backups/pre-upgrade_2025-01-19_20-30-15.sql (0.68 MB)
[4/5] Applying migrations...
  → 002 -> 003, add materials dataset
  → 003 -> 004, add csv_file_path to materials
  Completed in 0.45s
[5/5] Verifying migration state... ✓
  Current revision: 004abc1234 (head)

Database upgraded successfully!

Run rosemary db:status to verify the current state.
```

**Advantages over `flask db upgrade`:**
- Automatic backup before upgrading (safety!)
- Shows which migrations will be applied
- Better progress tracking
- Automatic rollback if migration fails
- Option to restore backup if something goes wrong

---

## Common Workflows

### First Time Setup (New Developer)

1. Clone the repository
2. Set up your `.env` file with database credentials
3. Activate virtual environment: `source venv/bin/activate`
4. Run: `rosemary db:setup`
5. Verify setup: `rosemary db:status`
6. Start the application: `flask run`

### Check Database Health

To quickly verify your database is properly configured and up to date:

```bash
rosemary db:status
```

This will show you connection status, current migration, and any pending updates.

### Creating and Applying Migrations

When you make changes to your models, create and apply migrations:

```bash
# 1. Make changes to your models (e.g., add a new field)
# 2. Create migration
rosemary db:migrate "add new field to model"

# 3. Review the generated migration file
# 4. Apply migration
rosemary db:upgrade

# 5. Verify
rosemary db:status
```

### Reset Database and Start Fresh

If you need to completely reset your database and reload seed data:

```bash
rosemary db:reset -y
rosemary db:seed -y
```

Or in one command:
```bash
rosemary db:seed --reset -y
```

### Clean Database (No Data)

If you need clean tables without any data:

```bash
rosemary db:reset -y
```

### Recreate Database from Scratch

If you need to rebuild the entire database schema:

```bash
rosemary db:reset --clear-migrations -y
rosemary db:seed -y
```

---

## Troubleshooting

### Migrations Fail

If migrations fail, check:
- Database connection in `.env` file
- Database server is running
- User has proper permissions

### Seed Data Fails

If seeding fails, check:
- Tables were created correctly (run migrations first)
- No conflicting data exists (try `db:reset` first)
- Check seeder error messages for specific issues

### Start Completely Fresh

To completely reset everything:

```bash
rosemary db:reset --clear-migrations -y
rosemary db:setup -y
```

---

## Command Options Reference

| Command | Options | Description |
|---------|---------|-------------|
| `db:setup` | `-y, --yes` | Skip confirmation prompt |
| `db:migrate` | `MESSAGE` (required) | Create new migration after model changes |
| `db:upgrade` | `--no-backup` | Skip automatic backup |
| `db:seed` | `-y, --yes` | Skip confirmation prompt |
| | `--reset` | Reset database before seeding |
| | `[MODULE]` | Seed only specific module |
| `db:reset` | `-y, --yes` | Skip confirmation prompt |
| | `--clear-migrations` | Remove and recreate migrations |
| `db:status` | (none) | Display database status information |

---

## Notes

- `db:upgrade` creates automatic backups in the `backups/` directory before applying migrations
- Use `--no-backup` flag only if you're certain and have another backup method
- Always backup your database before running reset commands
- The `-y` flag skips confirmation prompts (useful for automation)
- Seeders run in priority order defined in each seeder class
- All commands can be run with `--help` for more information
- Flask native commands (`flask db migrate`, `flask db upgrade`) still work, but Rosemary commands provide better UX
