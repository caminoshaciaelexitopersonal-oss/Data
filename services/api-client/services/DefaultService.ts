/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatAgentRequest } from '../models/ChatAgentRequest';
import type { QualityReport } from '../models/QualityReport';
import type { Session } from '../models/Session';
import type { SessionRequest } from '../models/SessionRequest';
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
