import { apiClient, unwrap } from '../client'
import type { components } from '../types/generated'
import type { ApiResponse } from '../types/http'

type Schemas = components['schemas']

export type ReportPeriod = Schemas['ReportPeriod']
export type ReportResponse = Schemas['ReportResponse']
export type GenerateReportRequest = Schemas['GenerateReportRequest']

export async function listReportPeriods(): Promise<ReportPeriod[]> {
  const response = await apiClient.get<ApiResponse<ReportPeriod[]>>(
    '/reports/periods',
  )
  return unwrap(response)
}

export async function generateReport(
  period: ReportPeriod,
): Promise<ReportResponse> {
  const response = await apiClient.post<ApiResponse<ReportResponse>>(
    '/reports/generate',
    { period } satisfies GenerateReportRequest,
  )
  return unwrap(response)
}
