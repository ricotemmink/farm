import { useCallback, useEffect, useState } from 'react'
import { FileText, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ErrorBanner } from '@/components/ui/error-banner'
import { EmptyState } from '@/components/ui/empty-state'
import { ListHeader } from '@/components/ui/list-header'
import { SectionCard } from '@/components/ui/section-card'
import { Skeleton } from '@/components/ui/skeleton'
import { useToastStore } from '@/stores/toast'
import {
  generateReport,
  listReportPeriods,
  type ReportPeriod,
  type ReportResponse,
} from '@/api/endpoints/reports'
import { createLogger } from '@/lib/logger'
import { getErrorMessage } from '@/utils/errors'
import { formatDateTime } from '@/utils/format'

const log = createLogger('ReportsPage')

interface GeneratedReportState {
  period: ReportPeriod
  response: ReportResponse
}

export default function ReportsPage() {
  const [periods, setPeriods] = useState<readonly ReportPeriod[] | null>(null)
  const [loadingPeriods, setLoadingPeriods] = useState(true)
  const [periodsError, setPeriodsError] = useState<string | null>(null)
  const [generating, setGenerating] = useState<ReportPeriod | null>(null)
  const [report, setReport] = useState<GeneratedReportState | null>(null)
  const toast = useToastStore((state) => state.add)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const result = await listReportPeriods()
        if (!cancelled) {
          setPeriods(result)
          setPeriodsError(null)
        }
      } catch (err) {
        log.error('listReportPeriods', err)
        if (!cancelled) {
          setPeriodsError(getErrorMessage(err))
        }
      } finally {
        if (!cancelled) {
          setLoadingPeriods(false)
        }
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const handleGenerate = useCallback(
    async (period: ReportPeriod) => {
      setGenerating(period)
      try {
        const response = await generateReport(period)
        setReport({ period, response })
        toast({
          variant: 'success',
          title: 'Report generated',
          description: `${period} report ready.`,
        })
      } catch (err) {
        log.error('generateReport', err)
        toast({
          variant: 'error',
          title: 'Report generation failed',
          description: getErrorMessage(err),
        })
      } finally {
        setGenerating(null)
      }
    },
    [toast],
  )

  return (
    <div className="space-y-section-gap p-card">
      <ListHeader
        title="Reports"
        count={periods?.length}
        description="Generate on-demand spending, performance, and task completion summaries for a chosen reporting period."
      />

      {periodsError ? (
        <ErrorBanner
          severity="error"
          title="Could not load report periods"
          description={periodsError}
          onRetry={() => {
            setLoadingPeriods(true)
            setPeriodsError(null)
            void listReportPeriods()
              .then((result) => setPeriods(result))
              .catch((err) => setPeriodsError(getErrorMessage(err)))
              .finally(() => setLoadingPeriods(false))
          }}
        />
      ) : loadingPeriods ? (
        <div className="grid grid-cols-1 gap-grid-gap sm:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      ) : periods && periods.length > 0 ? (
        <div className="grid grid-cols-1 gap-grid-gap sm:grid-cols-2 lg:grid-cols-3">
          {periods.map((period) => (
            <SectionCard
              key={period}
              title={period.charAt(0).toUpperCase() + period.slice(1)}
              icon={FileText}
            >
              <Button
                size="sm"
                onClick={() => void handleGenerate(period)}
                disabled={generating !== null}
              >
                <Play className="size-3" />
                {generating === period ? 'Generating…' : 'Generate'}
              </Button>
            </SectionCard>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FileText}
          title="No report periods available"
          description="The report service has not published any periods yet."
        />
      )}

      {report ? (
        <SectionCard
          title={`Latest ${report.period} report`}
          icon={FileText}
        >
          <dl className="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-text-muted">Start</dt>
              <dd className="font-mono">{formatDateTime(report.response.start)}</dd>
            </div>
            <div>
              <dt className="text-text-muted">End</dt>
              <dd className="font-mono">{formatDateTime(report.response.end)}</dd>
            </div>
            <div>
              <dt className="text-text-muted">Sections present</dt>
              <dd>
                <ul className="list-disc pl-4">
                  <li>Spending: {report.response.has_spending ? 'yes' : 'no'}</li>
                  <li>Performance: {report.response.has_performance ? 'yes' : 'no'}</li>
                  <li>
                    Task completion:{' '}
                    {report.response.has_task_completion ? 'yes' : 'no'}
                  </li>
                  <li>Risk trends: {report.response.has_risk_trends ? 'yes' : 'no'}</li>
                </ul>
              </dd>
            </div>
            <div>
              <dt className="text-text-muted">Generated at</dt>
              <dd className="font-mono">
                {formatDateTime(report.response.generated_at)}
              </dd>
            </div>
          </dl>
        </SectionCard>
      ) : null}
    </div>
  )
}
