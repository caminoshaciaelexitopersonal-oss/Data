/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatAgentRequest } from '../models/ChatAgentRequest';
import type { Job } from '../models/Job';
import type { QualityReport } from '../models/QualityReport';
import type { Session } from '../models/Session';
import type { SessionRequest } from '../models/SessionRequest';
import type { Step } from '../models/Step';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Create Session
     * @returns Session Session created successfully.
     * @throws ApiError
     */
    public static createSession(): CancelablePromise<Session> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/session/create',
        });
    }
    /**
     * Get Session
     * @param sessionId
     * @returns Session Session retrieved successfully.
     * @throws ApiError
     */
    public static getSession(
        sessionId: string,
    ): CancelablePromise<Session> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/mcp/session/{session_id}',
            path: {
                'session_id': sessionId,
            },
            errors: {
                404: `Session not found.`,
            },
        });
    }
    /**
     * Create Job
     * @param requestBody
     * @returns Job Job created successfully.
     * @throws ApiError
     */
    public static createJob(
        requestBody: {
            session_id: string;
            job_type: string;
        },
    ): CancelablePromise<Job> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/job/start',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Session not found.`,
            },
        });
    }
    /**
     * Create Step
     * @param requestBody
     * @returns Step Step created successfully.
     * @throws ApiError
     */
    public static createStep(
        requestBody: {
            job_id: string;
            description: string;
            payload?: Record<string, any> | null;
        },
    ): CancelablePromise<Step> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/step',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Job not found.`,
            },
        });
    }
    /**
     * Upload File
     * @param formData
     * @returns any File uploaded and processed successfully.
     * @throws ApiError
     */
    public static uploadFile(
        formData: {
            session_id?: string;
            file?: Blob;
        },
    ): CancelablePromise<{
        message?: string;
        filename?: string;
    }> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/ingestion/upload-file/',
            formData: formData,
            mediaType: 'multipart/form-data',
        });
    }
    /**
     * Get Data Quality Report
     * @param requestBody
     * @returns QualityReport Data quality report generated successfully.
     * @throws ApiError
     */
    public static getQualityReport(
        requestBody: SessionRequest,
    ): CancelablePromise<QualityReport> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/quality/report',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Chat with Agent
     * @param requestBody
     * @returns any Agent response.
     * @throws ApiError
     */
    public static chatAgent(
        requestBody: ChatAgentRequest,
    ): CancelablePromise<{
        output?: string;
    }> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/chat',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
