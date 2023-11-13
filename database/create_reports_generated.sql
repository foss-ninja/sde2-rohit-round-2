CREATE TABLE reports_generated(
    report_id UUID PRIMARY KEY,
    s3_object_key VARCHAR (255) NOT NULL,
    s3_bucket VARCHAR (255) NOT NULL,
    report_date DATE NOT NULL,
    report_type VARCHAR (255) NOT NULL,
    download_link TEXT NOT NULL
);