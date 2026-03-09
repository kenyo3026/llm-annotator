.PHONY: check-brew
check-brew:
	@which brew > /dev/null || (echo "Homebrew not found. Please install it first." && exit 1)

.PHONY: check-postgres
check-postgres:
	@which postgres > /dev/null || (echo "Homebrew not found. Please install it first." && exit 1)

.PHONY: install-postgres
install-postgres: check-brew
	@if brew list postgresql@14 > /dev/null 2>&1; then \
		echo "PostgreSQL @14 is already installed. Skipping installation."; \
	else \
		echo "Installing PostgreSQL @14..."; \
		brew install postgresql@14; \
	fi
	@if brew services list | grep postgresql@14 | grep started > /dev/null 2>&1; then \
		echo "PostgreSQL service is already running."; \
	else \
		echo "Starting PostgreSQL service..."; \
		brew services start postgresql@14; \
	fi

.PHONY: force-install-postgres
force-install-postgres: check-brew
	@echo "Force reinstalling PostgreSQL @14..."
	brew reinstall postgresql@14
	brew services restart postgresql@14
	@echo "PostgreSQL reinstalled and restarted!"

DB_NAME ?= test_db

.PHONY: setup-db
setup-db:
	createdb $(DB_NAME) || true
	psql postgres -c "CREATE USER myuser WITH PASSWORD 'mypassword';" || true
	psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $(DB_NAME) TO myuser;" || true
	@echo "Database '$(DB_NAME)' setup complete!"

.PHONY: init-schema
init-schema:
	@echo "Initializing schema for database: $(DB_NAME)"
	psql -d $(DB_NAME) -f db/feedback.sql
	psql -d $(DB_NAME) -f db/messages.sql
	psql -d $(DB_NAME) -f db/tags.sql
	psql -d $(DB_NAME) -c "GRANT ALL ON feedbacks, messages, tags TO myuser;" || true
	psql -d $(DB_NAME) -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO myuser;" || true
	@echo "Schema initialization complete for $(DB_NAME)!"

.PHONY: reset-messages
reset-messages:
	@echo "Dropping and recreating messages table in database: $(DB_NAME)"
	psql -d $(DB_NAME) -c "DROP TABLE IF EXISTS messages CASCADE;"
	psql -d $(DB_NAME) -f db/messages.sql
	@echo "Messages table reset complete!"

.PHONY: seed
seed: reset-messages
	@echo "Uploading seed data to database: $(DB_NAME)"
	DB_NAME=$(DB_NAME) uv run python scripts/seed_mock_data.py
	@echo "Seed data loaded!"

DUMP_FILE ?= data/feedbacks_dump.jsonl

.PHONY: dump-feedbacks
dump-feedbacks:
	@mkdir -p data
	@echo "Dumping feedbacks from $(DB_NAME) to $(DUMP_FILE)..."
	psql -d $(DB_NAME) -t -A -c \
		"SELECT row_to_json(feedbacks) FROM feedbacks ORDER BY id;" \
		> $(DUMP_FILE)
	@echo "Done! Saved to $(DUMP_FILE) ($(shell wc -l < $(DUMP_FILE)) rows)"

.PHONY: annotate
annotate:
	@echo "Running annotation pipeline against database: $(DB_NAME)"
	DB_NAME=$(DB_NAME) uv run pytest src/annotator/tests/test_annotation_pipeline.py::TestAnnotationPipeline::test_persist_pipeline -v -s
	@echo "Annotation pipeline complete!"

.PHONY: all
all: install-postgres setup-db init-schema