# Report on Missing Backend Endpoints

This document lists the frontend features that are currently non-functional due to the absence of corresponding backend endpoints in the new MPA (Modular Process Architecture).

The frontend code for these features exists, but the API calls they make result in "Not Found" errors because the backend routes have not been implemented yet.

## Missing Endpoints:

1.  **Multi-File Upload**
    *   **Frontend Function:** `handleMultiFileLoad` in `App.tsx`
    *   **Endpoint Called:** `POST /upload/multi`
    *   **Status:** This endpoint does not exist. The current ingestion MPA only supports single file uploads.

2.  **MongoDB Connection**
    *   **Frontend Function:** `handleMongoDbConnect` in `App.tsx`
    *   **Endpoint Called:** `POST /load-from-mongodb/`
    *   **Status:** This endpoint does not exist. There is no MPA for connecting to and ingesting from MongoDB.

3.  **S3 Connection**
    *   **Frontend Function:** `handleS3Connect` in `App.tsx`
    *   **Endpoint Called:** `POST /load-from-s3/`
    *   **Status:** This endpoint does not exist. There is no MPA for connecting to and ingesting from S3.

4.  **Excel File Upload (Multi-Sheet Handling)**
    *   **Frontend Function:** `handleExcelFileLoad` and `handleSheetSelection` in `App.tsx`
    *   **Endpoint Called:** `POST /upload-data/`
    *   **Status:** This endpoint does not exist. The new ingestion MPA (`/mpa/ingestion/upload-file/`) does not currently differentiate between file types or handle Excel files with multiple sheets.

## Recommendation:

To restore full functionality, new MPAs must be developed to support these data ingestion methods. The frontend code can then be updated to call the new, correct endpoints.
