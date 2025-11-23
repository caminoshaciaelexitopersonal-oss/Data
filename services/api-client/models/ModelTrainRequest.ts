/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ModelTrainRequest = {
    session_id: string;
    model_type: ModelTrainRequest.model_type;
    target_column: string;
    feature_columns: Array<string>;
};
export namespace ModelTrainRequest {
    export enum model_type {
        RANDOM_FOREST = 'random_forest',
        SVM = 'svm',
        LINEAR_REGRESSION = 'linear_regression',
    }
}
