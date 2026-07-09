CREATE TABLE words (
    id BIGSERIAL PRIMARY KEY,
    lemma TEXT NOT NULL,
    normalized_lemma TEXT NOT NULL,
    part_of_speech TEXT,
    cefr_level TEXT,
    frequency_rank INTEGER,
    frequency_score NUMERIC(10, 4),
    difficulty_score NUMERIC(10, 4),
    source_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (normalized_lemma, part_of_speech)
);

CREATE TABLE word_sources (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_word TEXT,
    source_cefr_level TEXT,
    source_frequency_rank INTEGER,
    source_frequency_score NUMERIC(10, 4),
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (word_id, source_name)
);

CREATE TABLE pipeline_runs (
    id BIGSERIAL PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    source_name TEXT,
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    inserted_records INTEGER DEFAULT 0,
    updated_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);


CREATE TABLE word_topic_scores (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL REFERENCES words(id) ON DELETE CASCADE,

    topic_name TEXT NOT NULL,
    provider_name TEXT NOT NULL,

    score NUMERIC(10, 4) NOT NULL DEFAULT 0,
    evidence_count INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (word_id, topic_name, provider_name)
);

CREATE TABLE word_search_results (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL REFERENCES words(id) ON DELETE CASCADE,

    provider_name TEXT NOT NULL,
    query_text TEXT NOT NULL,

    result_rank INTEGER NOT NULL,
    title TEXT,
    snippet TEXT,
    url TEXT,
    domain TEXT,

    raw_payload JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (word_id, provider_name, result_rank)
);

CREATE TABLE word_usage_summaries (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL REFERENCES words(id) ON DELETE CASCADE,

    provider_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    prompt_version TEXT NOT NULL,

    summary TEXT NOT NULL,
    raw_payload JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (word_id, provider_name, model_name, prompt_version)
);

CREATE TABLE word_definitions (
    id BIGSERIAL PRIMARY KEY,
    word_id BIGINT NOT NULL REFERENCES words(id) ON DELETE CASCADE,

    provider_name TEXT NOT NULL,
    language_code TEXT NOT NULL DEFAULT 'en',

    phonetic TEXT,
    definition_summary TEXT,
    raw_payload JSONB NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (word_id, provider_name, language_code)
);


CREATE TABLE pipeline_logs (
    id BIGSERIAL PRIMARY KEY,
    pipeline_run_id BIGINT REFERENCES pipeline_runs(id) ON DELETE CASCADE,

    level TEXT NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    context JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);