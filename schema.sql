-- Student Admission System schema for PostgreSQL / Neon.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
        CREATE TYPE gender_enum AS ENUM ('Male', 'Female', 'Other');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'blood_group_enum') THEN
        CREATE TYPE blood_group_enum AS ENUM ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-');
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS students (
    student_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_name VARCHAR(150) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_enum NOT NULL,
    blood_group blood_group_enum,
    photo_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS guardians (
    guardian_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    father_name VARCHAR(150),
    mother_name VARCHAR(150),
    mobile_number VARCHAR(15) NOT NULL,
    alternate_mobile VARCHAR(15),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_guardian_student UNIQUE (student_id)
);

CREATE TABLE IF NOT EXISTS addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    village_or_road VARCHAR(200),
    post_office VARCHAR(100),
    police_station VARCHAR(100),
    district VARCHAR(100),
    pin_code VARCHAR(10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_address_student UNIQUE (student_id)
);

CREATE TABLE IF NOT EXISTS schools (
    school_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_name VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS batches (
    batch_id SERIAL PRIMARY KEY,
    batch_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS academic_details (
    academic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    school_id UUID REFERENCES schools(school_id),
    class_id INT REFERENCES classes(class_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_academic_student UNIQUE (student_id)
);

CREATE TABLE IF NOT EXISTS academy_details (
    academy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    admission_date DATE NOT NULL,
    batch_id INT REFERENCES batches(batch_id),
    course_id INT REFERENCES courses(course_id),
    monthly_fee NUMERIC(10, 2) NOT NULL CHECK (monthly_fee >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_academy_student UNIQUE (student_id)
);

CREATE INDEX IF NOT EXISTS idx_students_name ON students(student_name);
CREATE INDEX IF NOT EXISTS idx_guardians_mobile ON guardians(mobile_number);
CREATE INDEX IF NOT EXISTS idx_addresses_pincode ON addresses(pin_code);
CREATE INDEX IF NOT EXISTS idx_academy_admission_date ON academy_details(admission_date);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_students_updated_at ON students;
CREATE TRIGGER trg_students_updated_at BEFORE UPDATE ON students
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_guardians_updated_at ON guardians;
CREATE TRIGGER trg_guardians_updated_at BEFORE UPDATE ON guardians
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_addresses_updated_at ON addresses;
CREATE TRIGGER trg_addresses_updated_at BEFORE UPDATE ON addresses
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_academic_updated_at ON academic_details;
CREATE TRIGGER trg_academic_updated_at BEFORE UPDATE ON academic_details
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_academy_updated_at ON academy_details;
CREATE TRIGGER trg_academy_updated_at BEFORE UPDATE ON academy_details
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE VIEW admission_full_view AS
SELECT
    s.student_id, s.student_name, s.date_of_birth,
    s.gender, s.blood_group, s.photo_url,
    g.father_name, g.mother_name, g.mobile_number, g.alternate_mobile,
    a.village_or_road, a.post_office, a.police_station, a.district, a.pin_code,
    sc.school_name, cl.class_name,
    ad.admission_date, b.batch_name, co.course_name, ad.monthly_fee
FROM students s
LEFT JOIN guardians g ON g.student_id = s.student_id
LEFT JOIN addresses a ON a.student_id = s.student_id
LEFT JOIN academic_details acd ON acd.student_id = s.student_id
LEFT JOIN schools sc ON sc.school_id = acd.school_id
LEFT JOIN classes cl ON cl.class_id = acd.class_id
LEFT JOIN academy_details ad ON ad.student_id = s.student_id
LEFT JOIN batches b ON b.batch_id = ad.batch_id
LEFT JOIN courses co ON co.course_id = ad.course_id;
