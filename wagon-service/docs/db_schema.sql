-- =============================================================
-- DDL: wagon_service schema
-- PostgreSQL 15+
-- Соответствует миграции 0013_wagon_todo_col_123
-- =============================================================

CREATE SCHEMA IF NOT EXISTS wagon_service;

SET search_path = wagon_service;

-- =============================================================
-- TABLE: wagon
-- =============================================================

CREATE TABLE wagon_service.wagon (
    -- Идентификация
    id                            UUID            NOT NULL DEFAULT gen_random_uuid(),
    external_id_rwl               VARCHAR(64)     NOT NULL,
    number                        VARCHAR(32)     NOT NULL,

    -- Классификация
    owner_type                    VARCHAR(32)     NOT NULL,
    wagon_type                    VARCHAR(32)     NOT NULL,
    model                         VARCHAR(64),

    -- Технические характеристики
    capacity_tons                 NUMERIC(10, 2),
    volume_m3                     NUMERIC(10, 2),

    -- Местоположение
    current_country               VARCHAR(64),
    current_station_code          VARCHAR(16),
    current_station_name          VARCHAR(255),
    current_city                  VARCHAR(255),

    -- Станция и дорога назначения (колонки UI / поле сортировки по умолчанию)
    destination_station_name      VARCHAR(255),
    destination_railway           VARCHAR(255),

    -- Следующая станция назначения (источник — RWL)
    next_destination_station_code VARCHAR(16),
    next_destination_station_name VARCHAR(255),

    -- Дата последнего движения из RWL; days_without_movement вычисляется на BE
    last_movement_at              TIMESTAMPTZ,

    -- Наименование поставщика из RWL
    supplier_name                 VARCHAR(255),

    -- Статус и логика распределения
    status                        VARCHAR(32)     NOT NULL,
    -- Вычисляется синхронизатором: true если есть незакрытая заявка без вагона
    -- и вагон подходит по критериям. Не GENERATED — логика пересекает wagon + request.
    requires_assignment           BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Мета
    source                        VARCHAR(32)     NOT NULL,  -- 'RWL' | 'RWL+1C'
    created_at                    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at                    TIMESTAMPTZ,               -- soft delete

    CONSTRAINT pk_wagon PRIMARY KEY (id),
    CONSTRAINT uq_wagon_external_id_rwl UNIQUE (external_id_rwl),
    CONSTRAINT uq_wagon_number          UNIQUE (number)
);

COMMENT ON TABLE  wagon_service.wagon IS 'Актуальные данные о вагонах из RWL и 1С';
COMMENT ON COLUMN wagon_service.wagon.requires_assignment IS
    'Вычисляется синхронизатором: true если существует незакрытая заявка без назначенного вагона и вагон подходит по критериям';
COMMENT ON COLUMN wagon_service.wagon.last_movement_at IS
    'Дата и время последнего движения из RWL. days_without_movement вычисляется на BE: CURRENT_DATE - last_movement_at::date. Закрыто: TODO-COL-1';
COMMENT ON COLUMN wagon_service.wagon.supplier_name IS
    'Наименование поставщика из RWL. NULL если RWL не передаёт значение. Закрыто: TODO-COL-2';
COMMENT ON COLUMN wagon_service.wagon.next_destination_station_code IS
    'Код следующей станции назначения из RWL. Закрыто: TODO-COL-3';
COMMENT ON COLUMN wagon_service.wagon.next_destination_station_name IS
    'Наименование следующей станции назначения из RWL. Закрыто: TODO-COL-3';

-- =============================================================
-- TABLE: request
-- =============================================================

CREATE TABLE wagon_service.request (
    id                        UUID        NOT NULL DEFAULT gen_random_uuid(),
    external_id_1c            VARCHAR(64) NOT NULL,

    -- Клиент (источник — 1С)
    client_name               VARCHAR(255) NOT NULL,

    -- Параметры заявки
    required_wagon_type       VARCHAR(32)  NOT NULL,
    origin_station_code       VARCHAR(16)  NOT NULL,
    destination_station_code  VARCHAR(16)  NOT NULL,
    planned_date              DATE         NOT NULL,

    -- NULL = вагон не назначен → участвует в вычислении requires_assignment
    wagon_assigned_id         UUID,

    -- Статус (зеркало 1С)
    status                    VARCHAR(32)  NOT NULL DEFAULT 'Новая',

    -- Мета
    created_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_request PRIMARY KEY (id),
    CONSTRAINT uq_request_external_id_1c UNIQUE (external_id_1c),
    CONSTRAINT fk_request_wagon_assigned_id_wagon
        FOREIGN KEY (wagon_assigned_id)
        REFERENCES wagon_service.wagon (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

COMMENT ON TABLE  wagon_service.request IS 'Агрегированные заявки из 1С для вычисления requires_assignment';
COMMENT ON COLUMN wagon_service.request.wagon_assigned_id IS
    'NULL = вагон не назначен; используется в вычислении wagon.requires_assignment';

-- =============================================================
-- TABLE: sync_log
-- =============================================================

CREATE TABLE wagon_service.sync_log (
    id              SERIAL       NOT NULL,
    source          VARCHAR(16)  NOT NULL,   -- 'RWL' | '1C'
    last_success_at TIMESTAMPTZ,             -- NULL если никогда не было успешной синхронизации
    last_status     VARCHAR(32)  NOT NULL,   -- 'success' | 'error' | 'running'
    last_error      TEXT,
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_sync_log         PRIMARY KEY (id),
    CONSTRAINT uq_sync_log_source  UNIQUE (source),
    CONSTRAINT sync_log_source_check CHECK (source IN ('RWL', '1C')),
    CONSTRAINT sync_log_status_check CHECK (last_status IN ('success', 'error', 'running'))
);

COMMENT ON TABLE  wagon_service.sync_log IS
    'Состояние последней синхронизации по источнику. Одна строка на источник (upsert).';
COMMENT ON COLUMN wagon_service.sync_log.last_success_at IS
    'NULL если синхронизация ещё не завершалась успешно';

-- Начальное заполнение при развёртывании
INSERT INTO wagon_service.sync_log (source, last_status)
VALUES ('RWL', 'error'), ('1C', 'error')
ON CONFLICT (source) DO NOTHING;

-- =============================================================
-- TRIGGER: auto-update updated_at в sync_log
-- =============================================================

CREATE OR REPLACE FUNCTION wagon_service.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_sync_log_updated_at
BEFORE UPDATE ON wagon_service.sync_log
FOR EACH ROW EXECUTE FUNCTION wagon_service.set_updated_at();

-- =============================================================
-- ИНДЕКСЫ: wagon
-- =============================================================

-- 1. Сортировка по умолчанию: destination_railway DESC, destination_station_name ASC
CREATE INDEX idx_wagon_sort_default
    ON wagon_service.wagon (destination_railway DESC NULLS LAST, destination_station_name ASC NULLS LAST)
    WHERE deleted_at IS NULL;

-- 2. Режим «Требующие распределения»
CREATE INDEX idx_wagon_requires_assignment
    ON wagon_service.wagon (requires_assignment)
    WHERE deleted_at IS NULL AND requires_assignment = TRUE;

-- 3. Фильтр «Дорога назначения»
CREATE INDEX idx_wagon_destination_railway
    ON wagon_service.wagon (destination_railway)
    WHERE deleted_at IS NULL;

-- 4. Фильтр «Поставщик»
CREATE INDEX idx_wagon_supplier_name
    ON wagon_service.wagon (supplier_name)
    WHERE deleted_at IS NULL;

-- 5. Фильтр «Статус»
CREATE INDEX idx_wagon_status
    ON wagon_service.wagon (status)
    WHERE deleted_at IS NULL;

-- 6. Фильтры owner_type / wagon_type
CREATE INDEX idx_wagon_owner_type
    ON wagon_service.wagon (owner_type)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_wagon_wagon_type
    ON wagon_service.wagon (wagon_type)
    WHERE deleted_at IS NULL;

-- 7. LIKE-поиск по номеру вагона (prefix)
CREATE INDEX idx_wagon_number_pattern
    ON wagon_service.wagon (number varchar_pattern_ops)
    WHERE deleted_at IS NULL;

-- 8. LIKE-поиск по станции назначения
CREATE INDEX idx_wagon_destination_station_name_pattern
    ON wagon_service.wagon (destination_station_name varchar_pattern_ops)
    WHERE deleted_at IS NULL;

-- 9. Комбинированный: requires_assignment + destination_railway
CREATE INDEX idx_wagon_assignment_railway
    ON wagon_service.wagon (requires_assignment, destination_railway)
    WHERE deleted_at IS NULL;

-- 10. current_city — из SRS п. 2.2.5
CREATE INDEX idx_wagon_current_city
    ON wagon_service.wagon (current_city)
    WHERE deleted_at IS NULL;

-- 11. updated_at — инкрементальная синхронизация
CREATE INDEX idx_wagon_updated_at
    ON wagon_service.wagon (updated_at DESC);

-- 12a. last_movement_at — сортировка по «Дням без движения» (TODO-COL-1)
CREATE INDEX idx_wagon_last_movement_at
    ON wagon_service.wagon (last_movement_at)
    WHERE deleted_at IS NULL;

-- 12b. next_destination_station_name — фильтрация по следующей станции (TODO-COL-3)
CREATE INDEX idx_wagon_next_destination
    ON wagon_service.wagon (next_destination_station_name)
    WHERE deleted_at IS NULL;

-- =============================================================
-- ИНДЕКСЫ: request
-- =============================================================

-- 12. FK к wagon — ON DELETE SET NULL без sequential scan
CREATE INDEX idx_request_wagon_assigned_id
    ON wagon_service.request (wagon_assigned_id)
    WHERE wagon_assigned_id IS NOT NULL;

-- 13. Незакрытые заявки без вагона — ядро вычисления requires_assignment
CREATE INDEX idx_request_unassigned
    ON wagon_service.request (status, planned_date)
    WHERE wagon_assigned_id IS NULL;

-- 14. Фильтр «Клиент»
CREATE INDEX idx_request_client_name
    ON wagon_service.request (client_name);

-- 15. external_id_1c покрыт UNIQUE constraint — отдельный индекс не нужен

-- =============================================================
-- Таблица соответствия: UI-фильтр → индекс
-- =============================================================
-- UI-фильтр / операция          | Поле запроса               | Индекс
-- -------------------------------|----------------------------|-----------------------------------------
-- Сортировка по умолчанию        | destination_railway DESC   | idx_wagon_sort_default
-- Режим «Требует распределения»  | requires_assignment = TRUE | idx_wagon_requires_assignment
-- Фильтр «Дорога назначения»     | destination_railway IN     | idx_wagon_destination_railway
-- Фильтр «Поставщик»             | supplier_name IN           | idx_wagon_supplier_name
-- Фильтр «Статус»                | status IN                  | idx_wagon_status
-- Фильтр «Тип вагона»            | wagon_type IN              | idx_wagon_wagon_type
-- Фильтр «Тип владения»          | owner_type IN              | idx_wagon_owner_type
-- Поиск по номеру (prefix)       | number LIKE 'X%'           | idx_wagon_number_pattern
-- Поиск по станции назначения    | destination_station_name ~ | idx_wagon_destination_station_name_pattern
-- Инкр. синхронизация            | updated_at > :ts           | idx_wagon_updated_at
-- Режим + дорога (комбо)         | requires_assignment + rail | idx_wagon_assignment_railway
-- Фильтр «Клиент» (request)      | client_name IN             | idx_request_client_name
-- Вычисление requires_assignment | wagon_assigned_id IS NULL  | idx_request_unassigned
