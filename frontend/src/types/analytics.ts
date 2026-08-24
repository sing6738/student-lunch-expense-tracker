export interface AnalyticsSummary {
  spent_today: number;
  spent_month: number;
  total_expenses: number;
}

export interface AnalyticsTrend {
  dates: string[];
  amounts: number[];
}

export interface AnalyticsCategory {
  category: string;
  amount: number;
}

export interface AnalyticsCalendar {
  date: string;
  amount: number;
}
